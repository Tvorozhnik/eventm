from django.shortcuts import render
from django.views.generic import View, ListView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from .models import Notification

# Create your views here.

class GetNotificationsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Получаем непрочитанные уведомления пользователя
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5]  # Показываем только 5 последних

        # Рендерим HTML для уведомлений
        notifications_html = render_to_string(
            'notifications/notifications_dropdown.html',
            {'notifications': notifications},
            request=request
        )

        return JsonResponse({
            'notifications_html': notifications_html,
            'unread_count': notifications.count()
        })

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification_id = kwargs.get('pk')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'status': 'success'})

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')
