from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3788d8')

    def __str__(self):
        return self.name

class Event(models.Model):
    # Удаляем EVENT_TYPES и заменяем на связь с EventCategory
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
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания")
    location = models.CharField(max_length=200, verbose_name="Место проведения")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_participants = models.PositiveIntegerField(default=0, verbose_name="Максимум участников")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    favorites = models.ManyToManyField('accounts.User', related_name='favorite_events_for_event', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена")
    image = models.ImageField(upload_to='events/', null=True, blank=True, verbose_name="Изображение")
    
    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ['-start_datetime']
    
    def __str__(self):
        return self.title