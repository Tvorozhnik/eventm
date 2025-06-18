from django.urls import path
from .views import (
    EventListView,
    EventCreateView,
    EventDetailView,
    EventUpdateView,
    EventDeleteView,
    ToggleFavoriteView,
    ApproveEventView,
    RejectEventView,
    ToggleRegistrationView,
)

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='events_list'),
    path('create/', EventCreateView.as_view(), name='events_create'),
    path('<int:pk>/', EventDetailView.as_view(), name='events_detail'),
    path('<int:pk>/edit/', EventUpdateView.as_view(), name='events_update'),
    path('<int:pk>/delete/', EventDeleteView.as_view(), name='events_delete'),
    path('<int:pk>/toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('<int:pk>/toggle-registration/', ToggleRegistrationView.as_view(), name='toggle_registration'),
    path('<int:pk>/approve/', ApproveEventView.as_view(), name='events_approve'),
    path('<int:pk>/reject/', RejectEventView.as_view(), name='events_reject'),
]