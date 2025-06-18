from django.urls import path
from .views import (
    GetNotificationsView, 
    MarkNotificationReadView, 
    MarkAllNotificationsReadView,
    NotificationListView
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('get/', GetNotificationsView.as_view(), name='get_notifications'),
    path('<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
] 