from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse

from repository.models import Document
from .models import Comment, Favourite, Notification
from .forms import CommentForm


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, slug):
        document = get_object_or_404(Document, slug=slug)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            
            # Handle reply to parent comment
            parent_id = form.cleaned_data.get('parent_id')
            if parent_id:
                parent_comment = Comment.objects.filter(id=parent_id, document=document).first()
                if parent_comment:
                    comment.parent = parent_comment
                    # Notify parent comment author
                    if parent_comment.user != request.user:
                        Notification.objects.create(
                            recipient=parent_comment.user,
                            actor=request.user,
                            verb=f"replied to your comment on '{document.title[:45]}...'",
                            target_url=document.get_absolute_url()
                        )

            comment.save()

            # Notify document uploader if different from commenter
            if document.uploaded_by != request.user and not parent_id:
                Notification.objects.create(
                    recipient=document.uploaded_by,
                    actor=request.user,
                    verb=f"commented on your paper '{document.title[:45]}...'",
                    target_url=document.get_absolute_url()
                )

            messages.success(request, "Your peer commentary has been added to the discussion.")
        else:
            messages.error(request, "Unable to post comment. Please provide valid commentary text.")

        return redirect('repository:document_detail', slug=slug)


class ToggleFavouriteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        document = get_object_or_404(Document, slug=slug)
        fav = Favourite.objects.filter(user=request.user, document=document).first()

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if fav:
            fav.delete()
            is_favourited = False
            msg = f"Removed '{document.title[:40]}...' from your saved favourites."
            messages.info(request, msg)
        else:
            Favourite.objects.create(user=request.user, document=document)
            is_favourited = True
            msg = f"Added '{document.title[:40]}...' to your saved research reading list."
            messages.success(request, msg)

        if is_ajax:
            return JsonResponse({'status': 'ok', 'is_favourited': is_favourited, 'message': msg})

        next_url = request.POST.get('next') or document.get_absolute_url()
        return HttpResponseRedirect(next_url)


class FavouriteListView(LoginRequiredMixin, ListView):
    model = Favourite
    template_name = 'collaboration/favourites_list.html'
    context_object_name = 'favourites'
    paginate_by = 10

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user).select_related('document', 'document__category')


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'collaboration/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def post(self, request, *args, **kwargs):
        # Mark all as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('collaboration:notifications')


class CollaborationHubView(TemplateView):
    template_name = 'collaboration/hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recent active discussion threads across all documents
        context['recent_comments'] = Comment.objects.filter(is_active=True).select_related('user', 'user__profile', 'document').order_by('-created_at')[:10]
        context['active_documents'] = Document.objects.filter(status=Document.STATUS_APPROVED, comments__isnull=False).distinct().order_by('-views')[:6]
        return context
