from django.urls import path
from .views import (
    AddCommentView, 
    ToggleFavouriteView, 
    FavouriteListView, 
    NotificationListView, 
    CollaborationHubView
)

app_name = 'collaboration'

urlpatterns = [
    path('', CollaborationHubView.as_view(), name='hub'),
    path('comment/<slug:slug>/', AddCommentView.as_view(), name='add_comment'),
    path('favourite/<slug:slug>/', ToggleFavouriteView.as_view(), name='toggle_favourite'),
    path('favourites/', FavouriteListView.as_view(), name='favourites_list'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]
