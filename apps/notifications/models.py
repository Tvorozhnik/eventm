from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Notification(models.Model):
    class Type(models.TextChoices):
        EVENT_CANCELLED = 'event_cancelled', 'Мероприятие отменено'
        EVENT_TIME_CHANGED = 'event_time_changed', 'Время мероприятия изменено'
        EVENT_UNPUBLISHED = 'event_unpublished', 'Мероприятие снято с публикации'
        SYSTEM = 'system', 'Системное уведомление'

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Получатель"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=Type.choices,
        verbose_name="Тип уведомления"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.recipient}"

    @classmethod
    def create_system_notification(cls, title, message, recipients=None):
        """
        Создает системное уведомление для всех пользователей или указанных получателей
        """
        if recipients is None:
            recipients = User.objects.all()

        notifications = []
        for recipient in recipients:
            notification = cls(
                recipient=recipient,
                notification_type=cls.Type.SYSTEM,
                title=title,
                message=message
            )
            notifications.append(notification)

        cls.objects.bulk_create(notifications)
        return notifications

    @classmethod
    def create_event_notification(cls, event, notification_type, old_start_time=None):
        """
        Создает уведомления о событии для зарегистрированных участников
        """
        # Получаем всех зарегистрированных участников
        recipients = event.registered_users.all()
        
        if not recipients.exists():
            return []

        notifications = []
        content_type = ContentType.objects.get_for_model(event)

        for recipient in recipients:
            title = f"{dict(cls.Type.choices)[notification_type]}: {event.title}"
            
            # Формируем сообщение в зависимости от типа уведомления
            if notification_type == cls.Type.EVENT_CANCELLED:
                message = f"Мероприятие '{event.title}' было отменено"
            elif notification_type == cls.Type.EVENT_TIME_CHANGED:
                old_time_str = old_start_time.strftime("%d.%m.%Y %H:%M") if old_start_time else "неизвестно"
                new_time_str = event.start_datetime.strftime("%d.%m.%Y %H:%M")
                message = f"Время проведения мероприятия '{event.title}' изменено с {old_time_str} на {new_time_str}"
            else:
                message = f"Мероприятие '{event.title}' снято с публикации"
            
            notification = cls(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                content_type=content_type,
                object_id=event.id
            )
            notifications.append(notification)

        cls.objects.bulk_create(notifications)
        return notifications
