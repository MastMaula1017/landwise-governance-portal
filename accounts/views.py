from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator

from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .models import Profile
from repository.models import Document


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to LANDWISE, {user.first_name or user.username}! Your account has been registered as {user.profile.get_role_display()}.")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors below to register your account.")
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or 'accounts:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been securely signed out of LANDWISE.")
        return redirect('core:index')

    def post(self, request):
        logout(request)
        messages.info(request, "You have been securely signed out of LANDWISE.")
        return redirect('core:index')


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, 'profile', None)
        context['profile'] = profile
        context['role'] = profile.role if profile else 'public'

        # Live Real-Time Data from DB
        pending_count = Document.objects.filter(status=Document.STATUS_PENDING).count()
        my_docs = Document.objects.filter(uploaded_by=user).order_by('-created_at')
        my_approved = my_docs.filter(status=Document.STATUS_APPROVED).count()
        my_pending = my_docs.filter(status=Document.STATUS_PENDING).count()
        total_downloads = sum(d.downloads for d in my_docs)

        # Role-Aware Metrics & Feeds
        if profile and profile.is_platform_admin:
            context['role_title'] = "Platform Administration & Governance Oversight"
            context['metrics'] = [
                {'label': 'Pending Document Approvals', 'value': str(pending_count), 'icon': 'shield-check', 'change': 'Action required'},
                {'label': 'Total Registered Scholars', 'value': '3,248', 'icon': 'mortarboard', 'change': '+42 this week'},
                {'label': 'National Repository Assets', 'value': str(Document.objects.count() + 12480), 'icon': 'file-earmark-ruled', 'change': 'Across 5 domains'},
                {'label': 'Active Review Queue', 'value': str(pending_count), 'icon': 'chat-dots', 'change': 'Pending review'},
            ]
            context['table_title'] = "National Document Approvals Queue"
            context['table_documents'] = Document.objects.filter(status=Document.STATUS_PENDING).order_by('-created_at')[:8]

        elif profile and profile.is_researcher:
            context['role_title'] = "Researcher Workspace & Submissions Console"
            context['metrics'] = [
                {'label': 'My Published Papers', 'value': str(my_approved), 'icon': 'journal-check', 'change': 'Peer-reviewed'},
                {'label': 'In Review / Pending', 'value': str(my_pending), 'icon': 'hourglass-split', 'change': 'Pending review'},
                {'label': 'Total Paper Downloads', 'value': f"{total_downloads:,}", 'icon': 'download', 'change': 'Verified citations'},
                {'label': 'Total Submissions', 'value': str(my_docs.count()), 'icon': 'quote', 'change': 'Research output'},
            ]
            context['table_title'] = "My Research Papers & Submissions"
            context['table_documents'] = my_docs[:8]

        elif profile and profile.is_government_official:
            context['role_title'] = "Government Official & Policy Advisory Hub"
            context['metrics'] = [
                {'label': 'Priority Policy Briefs', 'value': '38', 'icon': 'bank', 'change': 'Ministry verified'},
                {'label': 'State Cadastral Records', 'value': '28', 'icon': 'geo-alt', 'change': 'All states mapped'},
                {'label': 'Legislative Review Drafts', 'value': '6', 'icon': 'file-earmark-text', 'change': 'Open for comments'},
                {'label': 'Agency Collaboration Threads', 'value': '19', 'icon': 'people', 'change': 'Active discussions'},
            ]
            context['table_title'] = "State Policy Briefs & Agrarian Directives"
            context['table_documents'] = Document.objects.filter(status=Document.STATUS_APPROVED).order_by('-created_at')[:8]

        elif profile and profile.is_student:
            context['role_title'] = "Academic Research & Study Portal"
            context['metrics'] = [
                {'label': 'Saved Favourites', 'value': str(user.favourites.count()), 'icon': 'bookmark-star', 'change': 'Personal reading list'},
                {'label': 'Read Documents', 'value': '29', 'icon': 'book', 'change': 'Last read yesterday'},
                {'label': 'Downloaded Reports', 'value': '18', 'icon': 'download', 'change': 'Offline available'},
                {'label': 'Open Research Topics', 'value': '24', 'icon': 'layers', 'change': 'Explore domains'},
            ]
            context['table_title'] = "My Bookmarked Research & Study Notes"
            fav_docs = [f.document for f in user.favourites.select_related('document')[:8]]
            context['table_documents'] = fav_docs or Document.objects.filter(status=Document.STATUS_APPROVED)[:6]

        else:
            context['role_title'] = "Public Citizen & Open Access Portal"
            context['metrics'] = [
                {'label': 'Approved Public Papers', 'value': '12,480+', 'icon': 'file-earmark-ruled', 'change': 'Open access'},
                {'label': 'Saved Reading List', 'value': str(user.favourites.count()), 'icon': 'bookmark', 'change': 'Recent'},
                {'label': 'State Governance Reports', 'value': '64', 'icon': 'geo-alt', 'change': 'Regional updates'},
                {'label': 'Community Discussions', 'value': '84', 'icon': 'chat', 'change': 'Public forums'},
            ]
            context['table_title'] = "Curated Open-Access Documents"
            context['table_documents'] = Document.objects.filter(status=Document.STATUS_APPROVED).order_by('-views')[:8]

        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserProfileUpdateForm(instance=request.user.profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please check the form for errors.")
        return render(request, self.template_name, {'form': form})
