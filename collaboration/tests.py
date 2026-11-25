from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import Profile
from repository.models import Category, Document
from .models import Comment, Favourite, Notification


class CollaborationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username="res1", password="pw")
        Profile.objects.filter(user=self.author).update(role=Profile.ROLE_RESEARCHER)
        self.reader = User.objects.create_user(username="stu1", password="pw")
        Profile.objects.filter(user=self.reader).update(role=Profile.ROLE_STUDENT)

        self.cat = Category.objects.create(name="Rural Development")
        self.doc = Document.objects.create(
            title="Village Commons Study",
            abstract="Grazing rights and panchayat commons.",
            authors="Prof. Nair",
            category=self.cat,
            uploaded_by=self.author,
            status=Document.STATUS_APPROVED,
            file=SimpleUploadedFile("commons.pdf", b"%PDF-1.4\n%%EOF"),
        )

    def test_comment_and_favourite_flow(self):
        self.client.force_login(self.reader)
        resp_comment = self.client.post(
            reverse("collaboration:add_comment", kwargs={"slug": self.doc.slug}),
            {"body": "Insightful methodology on commons."},
        )
        self.assertEqual(resp_comment.status_code, 302)
        self.assertEqual(Comment.objects.filter(document=self.doc).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.author).count(), 1)

        resp_fav = self.client.post(
            reverse("collaboration:toggle_favourite", kwargs={"slug": self.doc.slug})
        )
        self.assertEqual(resp_fav.status_code, 302)
        self.assertTrue(Favourite.objects.filter(user=self.reader, document=self.doc).exists())
