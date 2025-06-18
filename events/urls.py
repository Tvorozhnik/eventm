from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('create/', views.events_create, name='events_create'),
    path('<int:event_id>/', views.events_detail, name='events_detail'),
    path('<int:event_id>/edit/', views.events_edit, name='events_edit'),
    path('<int:event_id>/delete/', views.events_delete, name='events_delete'),
    path('<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('<int:event_id>/unregister/', views.unregister_from_event, name='unregister_from_event'),
] 