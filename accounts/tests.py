from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile


class AccountsRoleAndDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="gov_user", password="secret")
        profile = self.user.profile
        profile.role = Profile.ROLE_OFFICIAL
        profile.save()

    def test_profile_created_via_signal_and_role_properties(self):
        profile = self.user.profile
        self.assertTrue(profile.is_government_official)
        self.assertFalse(profile.is_platform_admin)
        self.assertFalse(profile.can_upload_documents)

    def test_authenticated_dashboard_and_profile_update(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Government Official")

        resp_profile = self.client.get(reverse("accounts:profile"))
        self.assertEqual(resp_profile.status_code, 200)
