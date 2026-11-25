from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_RESEARCHER = 'researcher'
    ROLE_OFFICIAL = 'official'
    ROLE_STUDENT = 'student'
    ROLE_PUBLIC = 'public'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Platform Administrator'),
        (ROLE_RESEARCHER, 'Research Scholar / Academician'),
        (ROLE_OFFICIAL, 'Government Official / Policymaker'),
        (ROLE_STUDENT, 'Student / University Scholar'),
        (ROLE_PUBLIC, 'Public User / Citizen'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PUBLIC)
    institution = models.CharField(max_length=255, blank=True, help_text="University, Ministry, Department or Organization")
    designation = models.CharField(max_length=150, blank=True, help_text="Job title or academic position")
    state_region = models.CharField(max_length=100, blank=True, help_text="State / Union Territory")
    bio = models.TextField(blank=True, max_length=600, help_text="Brief professional or research background")
    phone = models.CharField(max_length=25, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    @property
    def is_researcher(self):
        return self.role == self.ROLE_RESEARCHER

    @property
    def is_government_official(self):
        return self.role == self.ROLE_OFFICIAL

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_public_user(self):
        return self.role == self.ROLE_PUBLIC

    @property
    def can_upload_documents(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_RESEARCHER]

    @property
    def can_approve_documents(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    @property
    def can_collaborate_and_comment(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_RESEARCHER, self.ROLE_OFFICIAL]

    @property
    def role_badge_class(self):
        mapping = {
            self.ROLE_ADMIN: 'badge-role-admin',
            self.ROLE_RESEARCHER: 'badge-role-researcher',
            self.ROLE_OFFICIAL: 'badge-role-official',
            self.ROLE_STUDENT: 'badge-role-student',
            self.ROLE_PUBLIC: 'badge-role-public',
        }
        return mapping.get(self.role, 'badge-role-public')


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    elif not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)
