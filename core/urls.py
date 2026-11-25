from django.urls import path
from .views import LandingPageView, InfoPageView

app_name = 'core'

urlpatterns = [
    path('', LandingPageView.as_view(), name='index'),
    path('privacy/', InfoPageView.as_view(page_key='privacy'), name='privacy'),
    path('terms/', InfoPageView.as_view(page_key='terms'), name='terms'),
    path('accessibility/', InfoPageView.as_view(page_key='accessibility'), name='accessibility'),
]

