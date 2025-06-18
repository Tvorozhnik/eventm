from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.templatetags.static import static

User = get_user_model()

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3788d8')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        MODERATION = 'moderation', 'На модерации'
        PUBLISHED = 'published', 'Опубликовано'
        UNPUBLISHED = 'unpublished', 'Снято с публикации'

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория"
    )
    start_datetime = models.DateTimeField(verbose_name="Дата и время начала")
    location = models.CharField(max_length=200, verbose_name="Место проведения")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_participants = models.PositiveIntegerField(default=0, verbose_name="Максимум участников")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус"
    )
    favorites = models.ManyToManyField(
        'accounts.User',
        related_name='favorite_events_for_event',
        blank=True,
        verbose_name="Добавили в избранное"
    )
    registered_users = models.ManyToManyField(
        'accounts.User',
        related_name='registered_events',
        blank=True,
        verbose_name="Зарегистрированные участники"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена")
    image = models.ImageField(upload_to='events/', null=True, blank=True, verbose_name="Изображение")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ['-start_datetime']
    
    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    def can_edit(self, user):
        return user.is_superuser or (user.is_staff and self.organizer == user)

    def can_moderate(self, user):
        return user.is_superuser

    def is_registration_open(self):
        """Проверяет, открыта ли регистрация на мероприятие"""
        if self.status != self.Status.PUBLISHED:
            return False
        if self.max_participants > 0 and self.registered_users.count() >= self.max_participants:
            return False
        return self.start_datetime > timezone.now()

    def get_image_url(self):
        """Возвращает URL изображения мероприятия или заглушки"""
        if self.image and hasattr(self.image, 'url'):
            timestamp = int(timezone.now().timestamp())
            return f"{self.image.url}?v={timestamp}"
        return static('images/event-default.jpg')