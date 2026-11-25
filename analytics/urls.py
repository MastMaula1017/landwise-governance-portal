from django.urls import path
from .views import AnalyticsDashboardView, AnalyticsDataApiView

app_name = 'analytics'

urlpatterns = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('api/stats/', AnalyticsDataApiView.as_view(), name='api_stats'),
]
