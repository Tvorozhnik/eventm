from django.urls import path
from .views import (
    EventListView,
    EventCreateView,
    EventDetailView,
    EventUpdateView,
    ToggleFavoriteView,
)

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='events_list'),
    path('create/', EventCreateView.as_view(), name='events_create'),
    path('<int:pk>/', EventDetailView.as_view(), name='events_detail'),
    path('<int:pk>/edit/', EventUpdateView.as_view(), name='events_update'),
    path('<int:pk>/toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
]