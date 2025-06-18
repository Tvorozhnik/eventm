# type: ignore[attr-defined]
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    TemplateView,
    DeleteView,
    View,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Manager
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from typing import Type, ClassVar
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Event, EventCategory
from .forms import EventForm
from apps.notifications.models import Notification

# Add type hints for models
Event.objects: ClassVar[Manager[Event]]  # type: ignore
EventCategory.objects: ClassVar[Manager[EventCategory]]  # type: ignore

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем 3 ближайших опубликованных мероприятия
        context['latest_events'] = Event.objects.filter(
            status=Event.Status.PUBLISHED,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:3]
        return context

class EventListView(ListView):
    model = Event
    template_name = 'events/events_list.html'
    context_object_name = 'events'
    paginate_by = 9

    def get_paginate_by(self, queryset):
        # Получаем значение per_page из GET-параметров или используем значение по умолчанию
        per_page = self.request.GET.get('per_page', self.paginate_by)
        try:
            per_page = int(per_page)
            # Проверяем, что значение находится в допустимом диапазоне
            if per_page not in [9, 12, 24, 36]:
                per_page = self.paginate_by
        except (ValueError, TypeError):
            per_page = self.paginate_by
        return per_page

    def get_queryset(self):
        # Базовый queryset в зависимости от роли пользователя
        user = self.request.user
        if user.is_superuser:
            # Суперпользователь видит все мероприятия
            queryset = Event.objects.all()
        elif user.is_staff:
            # Staff видит свои мероприятия в любом статусе и опубликованные мероприятия
            queryset = Event.objects.filter(
                Q(organizer=user) |
                Q(status=Event.Status.PUBLISHED)
            )
        else:
            # Обычные пользователи видят только опубликованные мероприятия
            queryset = Event.objects.filter(status=Event.Status.PUBLISHED)
        
        # Фильтр по дате
        selected_date = self.request.GET.get('selected-date')
        if selected_date:
            try:
                date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_datetime__date=date)
            except ValueError:
                pass
        
        # Фильтр по категориям
        selected_categories = self.request.GET.getlist('category')
        if selected_categories:
            queryset = queryset.filter(category_id__in=selected_categories)

        # Фильтр по актуальности
        relevance = self.request.GET.get('relevance')
        today = timezone.now().date()
        if relevance == 'upcoming':
            queryset = queryset.filter(start_datetime__date__gte=today)
        elif relevance == 'past':
            queryset = queryset.filter(start_datetime__date__lt=today)

        # Фильтр по статусу (только для staff и superuser)
        if user.is_staff or user.is_superuser:
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)

        return queryset.order_by('start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('selected-date')
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_relevance'] = self.request.GET.get('relevance')
        context['selected_status'] = self.request.GET.get('status')
        context['categories'] = EventCategory.objects.all()
        context['per_page'] = self.get_paginate_by(self.get_queryset())
        context['statuses'] = Event.Status.choices if self.request.user.is_staff else None
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            events = self.get_queryset()
            return JsonResponse({
                'html': self.render_to_response({'events': events}).rendered_content
            })
        return super().get(request, *args, **kwargs)

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/events_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        # Определяем доступность мероприятия в зависимости от роли пользователя
        user = self.request.user
        if user.is_superuser:
            return Event.objects.all()
        elif user.is_staff:
            return Event.objects.filter(
                Q(organizer=user) |
                Q(status=Event.Status.PUBLISHED)
            )
        return Event.objects.filter(status=Event.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        user = self.request.user
        
        # Получаем похожие опубликованные мероприятия той же категории
        similar_events = Event.objects.filter(
            category=event.category,
            status=Event.Status.PUBLISHED
        ).exclude(
            id=event.id
        ).order_by('start_datetime')[:3]
        
        context['similar_events'] = similar_events
        context['can_edit'] = event.can_edit(user)
        context['can_moderate'] = event.can_moderate(user)
        context['is_registered'] = user.is_authenticated and event.registered_users.filter(id=user.id).exists()
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/events_form.html'
    success_url = reverse_lazy('events:events_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Мероприятие успешно создано!')
        return response

class StaffOrOrganizerMixin(UserPassesTestMixin):
    def test_func(self):
        event = self.get_object()
        return event.can_edit(self.request.user)

class EventUpdateView(LoginRequiredMixin, StaffOrOrganizerMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/events_form.html'
    context_object_name = 'event'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Получаем старое время из базы данных
        old_event = Event.objects.get(pk=self.get_object().pk)
        old_start_time = old_event.start_datetime
        
        # Проверяем, было ли удалено изображение
        if 'image-clear' in self.request.POST and old_event.image:
            try:
                import os
                old_image = old_event.image.path
                if os.path.exists(old_image):
                    os.remove(old_image)
                form.instance.image = None
            except Exception as e:
                print(f"Ошибка при удалении изображения: {e}")
        
        # Если загружено новое изображение
        if 'image' in form.changed_data and form.cleaned_data['image']:
            if old_event.image:
                try:
                    import os
                    old_image = old_event.image.path
                    if os.path.exists(old_image):
                        os.remove(old_image)
                except Exception as e:
                    print(f"Ошибка при удалении старого изображения: {e}")
        
        response = super().form_valid(form)
        
        # Проверяем, изменилось ли время проведения
        if old_start_time != form.instance.start_datetime:
            Notification.create_event_notification(
                form.instance,
                Notification.Type.EVENT_TIME_CHANGED,
                old_start_time=old_start_time
            )
        
        messages.success(self.request, 'Мероприятие успешно обновлено!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('events:events_detail', kwargs={'pk': self.object.pk})

class EventDeleteView(LoginRequiredMixin, StaffOrOrganizerMixin, DeleteView):
    model = Event
    template_name = 'events/events_confirm_delete.html'
    success_url = reverse_lazy('events:events_list')

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        # Создаем уведомление об отмене мероприятия
        Notification.create_event_notification(
            event,
            Notification.Type.EVENT_CANCELLED
        )
        return super().delete(request, *args, **kwargs)

@method_decorator(require_POST, name='dispatch')
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event_id = kwargs.get('pk')
        try:
            event = Event.objects.get(id=event_id)
            if request.user in event.favorites.all():
                event.favorites.remove(request.user)
                is_favorite = False
            else:
                event.favorites.add(request.user)
                is_favorite = True
            return JsonResponse({
                'status': 'success',
                'is_favorite': is_favorite
            })
        except Event.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Мероприятие не найдено'
            }, status=404)

class ModeratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class ApproveEventView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        event.status = Event.Status.PUBLISHED
        event.save()
        
        messages.success(request, 'Мероприятие одобрено и опубликовано.')
        return redirect('events:events_detail', pk=event.pk)

class RejectEventView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        event.status = Event.Status.DRAFT
        event.save()
        
        messages.warning(request, 'Мероприятие отклонено и возвращено в черновики.')
        return redirect('events:events_detail', pk=event.pk)

@method_decorator(require_POST, name='dispatch')
class ToggleRegistrationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        
        # Проверяем, что мероприятие опубликовано
        if event.status != Event.Status.PUBLISHED:
            return JsonResponse({
                'status': 'error',
                'message': 'Регистрация на это мероприятие недоступна.'
            }, status=400)
        
        # Проверяем регистрацию пользователя
        is_registered = event.registered_users.filter(id=request.user.id).exists()
        
        if is_registered:
            # Отменяем регистрацию
            event.registered_users.remove(request.user)
            message = 'Регистрация отменена'
        else:
            # Проверяем наличие свободных мест
            if event.max_participants > 0 and event.registered_users.count() >= event.max_participants:
                return JsonResponse({
                    'status': 'error',
                    'message': 'К сожалению, все места уже заняты.'
                }, status=400)
            
            # Регистрируем пользователя
            event.registered_users.add(request.user)
            message = 'Вы успешно зарегистрировались на мероприятие'
        
        return JsonResponse({
            'status': 'success',
            'is_registered': not is_registered,
            'message': message,
            'participants_count': event.registered_users.count()
        })