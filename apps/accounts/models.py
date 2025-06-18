from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email должен быть установлен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField('Имя', max_length=150, validators=[MinLengthValidator(2)])
    last_name = models.CharField('Фамилия', max_length=150, validators=[MinLengthValidator(2)])
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    avatar = models.ImageField(
        _('avatar'), 
        upload_to='avatars/', 
        null=True, 
        blank=True,
        help_text='Загрузите изображение для аватара'
    )
    bio = models.TextField('О себе', max_length=500, blank=True)
    favorite_events = models.ManyToManyField('events.Event', related_name='favorited_by', blank=True)

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ORGANIZER = 'organizer', 'Организатор'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField('Роль', max_length=10, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_organizer(self):
        return self.role == self.Role.ORGANIZER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_role_display(self):
        return dict(self.Role.choices).get(self.role, self.role)

    def get_unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()

    def save(self, *args, **kwargs):
        # Если это новый объект (еще не сохранен в базе)
        if self.pk is None:
            saved_avatar = False
        else:
            # Получаем текущий объект из базы
            try:
                current = User.objects.get(pk=self.pk)
                saved_avatar = current.avatar
            except User.DoesNotExist:
                saved_avatar = False

        # Если загружен новый аватар и был старый, удаляем старый файл
        if saved_avatar and self.avatar != saved_avatar:
            saved_avatar.delete(save=False)

        super().save(*args, **kwargs)

    def get_avatar_url(self):
        """Возвращает URL аватара пользователя или заглушки"""
        if self.avatar:
            return self.avatar.url
        return static('images/ghost-svgrepo-com.svg')
