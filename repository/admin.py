from django.contrib import admin
from .models import Category, Tag, Document


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'approved_documents_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'authors', 'geography_region', 'status', 'views', 'downloads', 'uploaded_by', 'created_at')
    list_filter = ('status', 'document_type', 'category', 'geography_region', 'created_at')
    search_fields = ('title', 'abstract', 'authors', 'institution', 'extracted_text')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('views', 'downloads', 'file_size', 'file_pages', 'created_at', 'updated_at')
