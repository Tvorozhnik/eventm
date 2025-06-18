# type: ignore[attr-defined]
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    TemplateView,
    DeleteView,
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
from .models import Event, EventCategory
from .forms import EventForm

# Add type hints for models
Event.objects: ClassVar[Manager[Event]]  # type: ignore
EventCategory.objects: ClassVar[Manager[EventCategory]]  # type: ignore

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем 3 ближайших опубликованных мероприятия
        context['latest_events'] = Event.objects.filter(
            is_published=True,
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
        queryset = Event.objects.filter(is_published=True)
        
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

        return queryset.order_by('start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('selected-date')
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_relevance'] = self.request.GET.get('relevance')
        context['categories'] = EventCategory.objects.all()
        context['per_page'] = self.get_paginate_by(self.get_queryset())
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Получаем похожие мероприятия (той же категории, кроме текущего)
        similar_events = Event.objects.filter(
            category=event.category,
            is_published=True
        ).exclude(
            id=event.id
        ).order_by('start_datetime')[:3]
        
        context['similar_events'] = similar_events
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/events_form.html'
    success_url = reverse_lazy('events:events_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

class StaffOrOrganizerMixin(UserPassesTestMixin):
    def test_func(self):
        event = self.get_object()
        return (
            self.request.user.is_staff or 
            self.request.user.is_superuser or 
            event.organizer == self.request.user
        )

class EventUpdateView(LoginRequiredMixin, StaffOrOrganizerMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/events_form.html'
    context_object_name = 'event'
    
    def get_success_url(self):
        messages.success(self.request, 'Мероприятие успешно обновлено!')
        return reverse_lazy('events:events_detail', kwargs={'pk': self.object.pk})

class EventDeleteView(LoginRequiredMixin, StaffOrOrganizerMixin, DeleteView):
    model = Event
    template_name = 'events/events_confirm_delete.html'
    success_url = reverse_lazy('events:events_list')

@method_decorator(require_POST, name='dispatch')
class ToggleFavoriteView(LoginRequiredMixin, TemplateView):
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
                'message': 'Event not found'
            }, status=404)