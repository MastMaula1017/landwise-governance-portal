from django.test import TestCase, Client
from django.urls import reverse


class AnalyticsAndCorePagesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_analytics_dashboard_and_stats_api(self):
        resp = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "cadastralMap")

        api_resp = self.client.get(reverse("analytics:api_stats"))
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.json()
        self.assertIn("total_approved", data)
        self.assertIn("logged_views", data)
        self.assertIn("logged_downloads", data)

    def test_footer_info_pages_render(self):
        for name in ("core:privacy", "core:terms", "core:accessibility"):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200)
