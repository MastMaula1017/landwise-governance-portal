import io
import zipfile
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import Profile
from .models import Category, Tag, Document, DocumentActivityLog
from .utils import (
    auto_categorize_document,
    auto_extract_keywords,
    extract_pdf_text_and_meta,
    generate_citations,
)


def make_test_docx_bytes(paragraph_text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body><w:p><w:r><w:t>{paragraph_text}</w:t></w:r></w:p></w:body>'
            '</w:document>'
        )
        zf.writestr('word/document.xml', xml)
    buf.seek(0)
    return buf.getvalue()


class RepositorySmartUtilsTests(TestCase):
    def test_auto_categorize_document(self):
        text = "Cadastral drone survey and land titling mutation registry for parcel boundary mapping."
        self.assertEqual(auto_categorize_document(text), "Land Ownership")

    def test_auto_extract_keywords(self):
        text = "Cadastral cadastral cadastral survey survey titling watershed governance"
        keywords = auto_extract_keywords(text, max_keywords=3)
        self.assertEqual(keywords[0], "cadastral")
        self.assertIn("survey", keywords)

    def test_docx_text_extraction(self):
        docx_bytes = make_test_docx_bytes("Agrarian land reform and groundwater tenancy policy.")
        uploaded = SimpleUploadedFile("brief.docx", docx_bytes, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        text, pages = extract_pdf_text_and_meta(uploaded)
        self.assertIn("Agrarian land reform", text)
        self.assertGreaterEqual(pages, 1)

    def test_generate_citations_formats(self):
        user = User.objects.create_user(username="author1", password="pw")
        cat = Category.objects.create(name="Land Reforms")
        doc = Document.objects.create(
            title="Tenancy Security Study",
            authors="Dr. A. Rao",
            institution="NILA",
            category=cat,
            uploaded_by=user,
            status=Document.STATUS_APPROVED,
            file=SimpleUploadedFile("test.pdf", b"%PDF-1.4\n%%EOF"),
        )
        citations = generate_citations(doc)
        self.assertIn("apa", citations)
        self.assertIn("mla", citations)
        self.assertIn("chicago", citations)
        self.assertIn("Tenancy Security Study", citations["apa"])


class RepositoryWorkflowAndPermissionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="adm", password="pw")
        self.admin.profile.role = Profile.ROLE_ADMIN
        self.admin.profile.save()

        self.researcher = User.objects.create_user(username="res", password="pw")
        self.researcher.profile.role = Profile.ROLE_RESEARCHER
        self.researcher.profile.save()

        self.student = User.objects.create_user(username="stu", password="pw")
        self.student.profile.role = Profile.ROLE_STUDENT
        self.student.profile.save()

        self.category = Category.objects.create(name="Land Ownership", order=1)
        self.pending_doc = Document.objects.create(
            title="Pending Cadastral Paper",
            abstract="Cadastral study abstract.",
            authors="Dr. Rao",
            category=self.category,
            uploaded_by=self.researcher,
            status=Document.STATUS_PENDING,
            file=SimpleUploadedFile("pending.pdf", b"%PDF-1.4\n%%EOF"),
        )
        self.approved_doc = Document.objects.create(
            title="Approved Forest Rights Paper",
            abstract="Forest rights and watershed governance.",
            authors="Dr. Sen",
            geography_region="Odisha",
            category=self.category,
            uploaded_by=self.researcher,
            status=Document.STATUS_APPROVED,
            file=SimpleUploadedFile("approved.pdf", b"%PDF-1.4\n%%EOF"),
        )

    def test_public_cannot_view_pending_document(self):
        resp = self.client.get(reverse("repository:document_detail", kwargs={"slug": self.pending_doc.slug}))
        self.assertEqual(resp.status_code, 404)

    def test_view_logs_activity_and_increments_views(self):
        url = reverse("repository:document_detail", kwargs={"slug": self.approved_doc.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.approved_doc.refresh_from_db()
        self.assertEqual(self.approved_doc.views, 1)
        self.assertEqual(
            DocumentActivityLog.objects.filter(document=self.approved_doc, action=DocumentActivityLog.ACTION_VIEW).count(),
            1,
        )

    def test_student_cannot_access_admin_approvals_or_categories(self):
        self.client.force_login(self.student)
        resp_app = self.client.get(reverse("repository:admin_approvals"))
        resp_cat = self.client.get(reverse("repository:admin_categories"))
        self.assertEqual(resp_app.status_code, 302)
        self.assertEqual(resp_cat.status_code, 302)

    def test_admin_can_approve_document_and_manage_categories(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("repository:document_review_action", kwargs={"slug": self.pending_doc.slug}),
            {"action": "approve"},
        )
        self.assertEqual(resp.status_code, 302)
        self.pending_doc.refresh_from_db()
        self.assertEqual(self.pending_doc.status, Document.STATUS_APPROVED)

        resp_cat = self.client.post(
            reverse("repository:admin_categories"),
            {"name": "Urban Land Policy", "description": "Urban zoning", "order": 5},
        )
        self.assertEqual(resp_cat.status_code, 302)
        self.assertTrue(Category.objects.filter(name="Urban Land Policy").exists())
