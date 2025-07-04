# Generated by Django 5.2.3 on 2025-06-17 03:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('event_type', models.CharField(choices=[('conference', 'Конференция'), ('workshop', 'Мастер-класс'), ('meetup', 'Встреча')], max_length=20, verbose_name='Тип мероприятия')),
                ('start_datetime', models.DateTimeField(verbose_name='Дата и время начала')),
                ('end_datetime', models.DateTimeField(verbose_name='Дата и время окончания')),
                ('location', models.CharField(max_length=200, verbose_name='Место проведения')),
                ('max_participants', models.PositiveIntegerField(default=0, verbose_name='Максимум участников')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
                'ordering': ['-start_datetime'],
            },
        ),
    ]
