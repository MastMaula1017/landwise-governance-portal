from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, F
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Document, Category, Tag, DocumentActivityLog
from .forms import DocumentUploadForm, DocumentApprovalForm, CategoryForm
from collaboration.models import Notification
from .utils import (
    extract_pdf_text_and_meta, 
    auto_extract_keywords, 
    auto_categorize_document, 
    get_related_documents, 
    generate_citations
)


class DocumentListView(ListView):
    model = Document
    template_name = 'repository/document_list.html'
    context_object_name = 'documents'
    paginate_by = 9

    def get_queryset(self):
        # Only show approved documents to public/normal users; admins can see pending/all
        qs = Document.objects.filter(status=Document.STATUS_APPROVED)
        
        # Search Query
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | 
                Q(abstract__icontains=q) | 
                Q(authors__icontains=q) |
                Q(institution__icontains=q) |
                Q(extracted_text__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()

        # Category Filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Document Type Filter
        doc_type = self.request.GET.get('type')
        if doc_type:
            qs = qs.filter(document_type=doc_type)

        # Geography Filter
        region = self.request.GET.get('region')
        if region:
            qs = qs.filter(geography_region__icontains=region)

        # Sorting
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'views':
            qs = qs.order_by('-views', '-created_at')
        elif sort == 'downloads':
            qs = qs.order_by('-downloads', '-created_at')
        elif sort == 'title':
            qs = qs.order_by('title')
        elif sort == 'oldest':
            qs = qs.order_by('created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['document_types'] = Document.TYPE_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_sort'] = self.request.GET.get('sort', 'newest')
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_region'] = self.request.GET.get('region', '')
        context['total_count'] = self.get_queryset().count()
        return context


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'repository/document_detail.html'
    context_object_name = 'document'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # If not approved, only uploader or admin can view
        if obj.status != Document.STATUS_APPROVED:
            if not self.request.user.is_authenticated:
                raise Http404("Document is currently under review.")
            is_uploader = obj.uploaded_by == self.request.user
            is_admin = getattr(self.request.user, 'profile', None) and self.request.user.profile.is_platform_admin
            if not (is_uploader or is_admin):
                raise Http404("Document is currently under review.")
        
        # Increment View Count atomically and record activity log
        Document.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        obj.refresh_from_db(fields=['views'])
        DocumentActivityLog.objects.create(
            document=obj,
            user=self.request.user if self.request.user.is_authenticated else None,
            action=DocumentActivityLog.ACTION_VIEW,
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = self.object
        context['related_documents'] = get_related_documents(doc, limit=3)
        context['citations'] = generate_citations(doc)
        context['approval_form'] = DocumentApprovalForm()
        return context


class DocumentDownloadView(View):
    def get(self, request, slug):
        doc = get_object_or_404(Document, slug=slug)
        if doc.status != Document.STATUS_APPROVED:
            is_authorized = request.user.is_authenticated and (
                doc.uploaded_by == request.user or 
                (hasattr(request.user, 'profile') and request.user.profile.is_platform_admin)
            )
            if not is_authorized:
                return HttpResponseForbidden("This document is pending approval.")

        # Increment download counter atomically and record activity log
        Document.objects.filter(pk=doc.pk).update(downloads=F('downloads') + 1)
        DocumentActivityLog.objects.create(
            document=doc,
            user=request.user if request.user.is_authenticated else None,
            action=DocumentActivityLog.ACTION_DOWNLOAD,
        )

        # Serve file
        try:
            return FileResponse(doc.file.open('rb'), as_attachment=True, filename=doc.file.name.split('/')[-1])
        except Exception:
            messages.error(request, "File could not be accessed on the server.")
            return redirect('repository:document_detail', slug=slug)


class DocumentUploadView(LoginRequiredMixin, View):
    template_name = 'repository/document_upload.html'

    def test_func(self):
        profile = getattr(self.request.user, 'profile', None)
        return profile and profile.can_upload_documents

    def get(self, request):
        if not self.test_func():
            messages.warning(request, "Your current account role does not have authorization to upload research papers.")
            return redirect('accounts:dashboard')
        form = DocumentUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not self.test_func():
            return HttpResponseForbidden("Unauthorized role.")

        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            
            # File size in bytes
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                doc.file_size = uploaded_file.size

            # Save instance to get storage path
            doc.save()

            # Smart PDF Extraction: Text, Page Count
            try:
                if doc.file and doc.file.path:
                    extracted_text, pages = extract_pdf_text_and_meta(doc.file.path)
                    doc.extracted_text = extracted_text
                    doc.file_pages = pages
                    
                    # Smart auto-categorization if user didn't choose one
                    if not doc.category and extracted_text:
                        suggested_cat_name = auto_categorize_document(extracted_text)
                        if suggested_cat_name:
                            cat = Category.objects.filter(name__icontains=suggested_cat_name).first()
                            if cat:
                                doc.category = cat
            except Exception:
                pass

            # Admin uploads are auto-approved; Researcher uploads require review
            profile = request.user.profile
            if profile.is_platform_admin:
                doc.status = Document.STATUS_APPROVED
                doc.reviewed_by = request.user
                doc.reviewed_at = timezone.now()
            else:
                doc.status = Document.STATUS_PENDING

            doc.save()

            # Handle Tags: User input or smart auto-extraction
            tag_input = form.cleaned_data.get('tag_input', '').strip()
            if tag_input:
                raw_tags = [t.strip() for t in tag_input.split(',') if t.strip()]
            elif doc.extracted_text:
                raw_tags = auto_extract_keywords(doc.extracted_text, max_keywords=5)
            else:
                raw_tags = []

            for tag_name in raw_tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name.title())
                doc.tags.add(tag)

            if doc.status == Document.STATUS_APPROVED:
                messages.success(request, f"Research paper '{doc.title}' has been successfully published!")
            else:
                messages.info(request, f"Research paper '{doc.title}' uploaded successfully and submitted for peer review.")
            
            return redirect('repository:document_detail', slug=doc.slug)
        else:
            messages.error(request, "Please review the errors in the form below.")
        return render(request, self.template_name, {'form': form})


class AdminApprovalListView(LoginRequiredMixin, View):
    template_name = 'repository/admin_approvals.html'

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not (profile and profile.can_approve_documents):
            messages.error(request, "Access restricted to Platform Administrators.")
            return redirect('accounts:dashboard')

        pending_docs = Document.objects.filter(status=Document.STATUS_PENDING).order_by('-created_at')
        rejected_docs = Document.objects.filter(status=Document.STATUS_REJECTED).order_by('-created_at')
        return render(request, self.template_name, {
            'pending_docs': pending_docs,
            'rejected_docs': rejected_docs,
        })


class DocumentApprovalActionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        profile = getattr(request.user, 'profile', None)
        if not (profile and profile.can_approve_documents):
            return HttpResponseForbidden("Unauthorized.")

        doc = get_object_or_404(Document, slug=slug)
        action = request.POST.get('action')
        reason = request.POST.get('rejection_reason', '').strip()

        if action == 'approve':
            doc.status = Document.STATUS_APPROVED
            doc.reviewed_by = request.user
            doc.reviewed_at = timezone.now()
            doc.rejection_reason = ''
            doc.save()
            if doc.uploaded_by != request.user:
                Notification.objects.create(
                    recipient=doc.uploaded_by,
                    actor=request.user,
                    verb=f"approved your research submission '{doc.title[:60]}'",
                    target_url=doc.get_absolute_url(),
                )
            messages.success(request, f"Document '{doc.title}' has been APPROVED and published to the national repository.")
        elif action == 'reject':
            doc.status = Document.STATUS_REJECTED
            doc.reviewed_by = request.user
            doc.reviewed_at = timezone.now()
            doc.rejection_reason = reason or "Editorial revision required."
            doc.save()
            if doc.uploaded_by != request.user:
                Notification.objects.create(
                    recipient=doc.uploaded_by,
                    actor=request.user,
                    verb=f"requested revisions on '{doc.title[:60]}'",
                    target_url=doc.get_absolute_url(),
                )
            messages.warning(request, f"Document '{doc.title}' status updated to REVISION REQUESTED.")

        return redirect('repository:admin_approvals')


class AdminCategoryManageView(LoginRequiredMixin, View):
    template_name = 'repository/admin_categories.html'

    def _is_admin(self, user):
        profile = getattr(user, 'profile', None)
        return profile and profile.is_platform_admin

    def get(self, request):
        if not self._is_admin(request.user):
            messages.error(request, "Access restricted to Platform Administrators.")
            return redirect('accounts:dashboard')
        categories = Category.objects.all()
        form = CategoryForm()
        return render(request, self.template_name, {'categories': categories, 'form': form})

    def post(self, request):
        if not self._is_admin(request.user):
            return HttpResponseForbidden("Unauthorized.")
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Policy category '{cat.name}' created successfully.")
            return redirect('repository:admin_categories')
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories, 'form': form})


class AdminCategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not (profile and profile.is_platform_admin):
            return HttpResponseForbidden("Unauthorized.")
        cat = get_object_or_404(Category, pk=pk)
        name = cat.name
        cat.delete()
        messages.info(request, f"Category '{name}' removed.")
        return redirect('repository:admin_categories')
