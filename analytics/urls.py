from django.urls import path
from .views import AnalyticsDashboardView, AnalyticsDataApiView, AnalyticsCsvExportView

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('api/stats/', AnalyticsDataApiView.as_view(), name='api_stats'),
    path('export-csv/', AnalyticsCsvExportView.as_view(), name='export_csv'),
]
