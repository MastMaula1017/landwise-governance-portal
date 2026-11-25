from django.urls import path
from .views import (
    DocumentListView, 
    DocumentDetailView, 
    DocumentDownloadView, 
    DocumentUploadView, 
    AdminApprovalListView, 
    DocumentApprovalActionView,
    AdminCategoryManageView,
    AdminCategoryDeleteView,
)

app_name = 'repository'

urlpatterns = [
    path('', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('approvals/', AdminApprovalListView.as_view(), name='admin_approvals'),
    path('categories/', AdminCategoryManageView.as_view(), name='admin_categories'),
    path('categories/<int:pk>/delete/', AdminCategoryDeleteView.as_view(), name='admin_category_delete'),
    path('<slug:slug>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<slug:slug>/download/', DocumentDownloadView.as_view(), name='document_download'),
    path('<slug:slug>/review/', DocumentApprovalActionView.as_view(), name='document_review_action'),
]
