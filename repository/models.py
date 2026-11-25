from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import os


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, default='bi-folder', help_text="Icon identifier or Bootstrap icon name")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def approved_documents_count(self):
        return self.documents.filter(status=Document.STATUS_APPROVED).count()


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Document(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Under Review'),
        (STATUS_APPROVED, 'Approved & Published'),
        (STATUS_REJECTED, 'Revision Requested'),
    ]

    TYPE_CHOICES = [
        ('research_paper', 'Peer-Reviewed Research Paper'),
        ('policy_brief', 'Government Policy Brief'),
        ('case_study', 'Empirical Case Study'),
        ('cadastral_directive', 'Cadastral & Legal Directive'),
        ('technical_report', 'Technical Survey Report'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    document_type = models.CharField(max_length=35, choices=TYPE_CHOICES, default='research_paper')
    abstract = models.TextField(help_text="Comprehensive executive summary or paper abstract")
    authors = models.CharField(max_length=300, help_text="e.g. Prof. A. N. Ramanathan, Dr. Sarah Jenkins")
    institution = models.CharField(max_length=250, blank=True, help_text="Lead university, research bureau or department")
    
    file = models.FileField(upload_to='research_documents/%Y/%m/', help_text="Upload PDF or DOCX research file")
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    file_pages = models.PositiveIntegerField(default=1, help_text="Extracted page count")
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='documents')
    tags = models.ManyToManyField(Tag, blank=True, related_name='documents')
    
    publication_date = models.DateField(null=True, blank=True, help_text="Original publication or study release date")
    geography_region = models.CharField(max_length=120, blank=True, default='National / All India', help_text="e.g. Maharashtra, Odisha, Central Agro-Climatic Zone")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    rejection_reason = models.TextField(blank=True, help_text="Review feedback or reasons for revision request")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_documents')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    
    extracted_text = models.TextField(blank=True, help_text="Extracted text from PDF for smart full-text search")
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:280]
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('repository:document_detail', kwargs={'slug': self.slug})

    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace('.', '')
        return ''

    @property
    def formatted_file_size(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{round(size / 1024, 1)} KB"
        else:
            return f"{round(size / (1024 * 1024), 2)} MB"

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_APPROVED:
            return 'bg-success-subtle text-success border border-success-subtle'
        elif self.status == self.STATUS_PENDING:
            return 'bg-warning-subtle text-warning-emphasis border border-warning-subtle'
        else:
            return 'bg-danger-subtle text-danger border border-danger-subtle'


class DocumentActivityLog(models.Model):
    ACTION_VIEW = 'view'
    ACTION_DOWNLOAD = 'download'
    ACTION_CHOICES = [
        (ACTION_VIEW, 'Document Viewed'),
        (ACTION_DOWNLOAD, 'Document Downloaded'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='document_activities')
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        actor = self.user.username if self.user else 'Anonymous'
        return f"{actor} {self.action} '{self.document.title[:35]}'"
