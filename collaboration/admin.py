from django.contrib import admin
from .models import Comment, Favourite, Notification


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'is_reply', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('body', 'user__username', 'document__title')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'created_at')
    search_fields = ('user__username', 'document__title')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'verb')
