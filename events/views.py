from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Event, Category
from .forms import EventForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    TemplateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from .models import EventCategory

def events_list(request):
    # Получаем параметры фильтрации
    selected_date = request.GET.get('selected-date')
    selected_categories = request.GET.getlist('category')
    selected_relevance = request.GET.get('relevance')
    per_page = request.GET.get('per_page', 12)

    # Базовый queryset
    events = Event.objects.filter(is_published=True).order_by('start_datetime')

    # Фильтр по дате
    if selected_date:
        try:
            date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            events = events.filter(start_datetime__date=date)
        except ValueError:
            pass

    # Фильтр по категориям
    if selected_categories:
        events = events.filter(category_id__in=selected_categories)

    # Фильтр по актуальности
    now = timezone.now()
    if selected_relevance == 'upcoming':
        events = events.filter(start_datetime__gte=now)
    elif selected_relevance == 'past':
        events = events.filter(start_datetime__lt=now)

    # Разделяем на активные и прошедшие мероприятия
    active_events = events.filter(start_datetime__gte=now)
    past_events = events.filter(start_datetime__lt=now)

    # Пагинация
    try:
        per_page = int(per_page)
        if per_page not in [12, 24, 36, 48]:
            per_page = 12
    except (ValueError, TypeError):
        per_page = 12

    # Контекст для шаблона
    context = {
        'active_events': active_events,
        'past_events': past_events,
        'events': events,
        'categories': EventCategory.objects.all(),
        'selected_date': selected_date,
        'selected_categories': selected_categories,
        'selected_relevance': selected_relevance,
        'per_page': per_page,
        'now': now,
    }

    return render(request, 'events/events_list.html', context)

@login_required
def events_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Мероприятие успешно создано')
            return redirect('events:events_detail', event.id)
    else:
        form = EventForm()
    return render(request, 'events/events_form.html', {'form': form, 'action': 'create'})

@login_required
def events_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer:
        messages.error(request, 'У вас нет прав для редактирования этого мероприятия')
        return redirect('events:events_detail', event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Мероприятие успешно обновлено')
            return redirect('events:events_detail', event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/events_form.html', {'form': form, 'action': 'edit'})

@login_required
def events_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer:
        messages.error(request, 'У вас нет прав для удаления этого мероприятия')
        return redirect('events:events_detail', event.id)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Мероприятие успешно удалено')
        return redirect('events:events_list')
    return render(request, 'events/events_confirm_delete.html', {'event': event})

def events_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/events_detail.html', {'event': event})

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.participants.filter(id=request.user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Вы уже зарегистрированы на это мероприятие'})
    
    if event.participants.count() >= event.max_participants:
        return JsonResponse({'status': 'error', 'message': 'Достигнуто максимальное количество участников'})
    
    event.participants.add(request.user)
    return JsonResponse({'status': 'success', 'message': 'Вы успешно зарегистрировались на мероприятие'})

@login_required
def unregister_from_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not event.participants.filter(id=request.user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Вы не зарегистрированы на это мероприятие'})
    
    event.participants.remove(request.user)
    return JsonResponse({'status': 'success', 'message': 'Вы успешно отменили регистрацию на мероприятие'})

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
    paginate_by = 12

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', self.paginate_by)
        try:
            per_page = int(per_page)
            if per_page not in [12, 24, 36, 48]:
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
        now = timezone.now()
        if relevance == 'upcoming':
            queryset = queryset.filter(start_datetime__gte=now)
        elif relevance == 'past':
            queryset = queryset.filter(start_datetime__lt=now)

        return queryset.order_by('start_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Получаем базовый queryset
        queryset = self.get_queryset()
        
        # Разделяем на активные и прошедшие мероприятия
        context['active_events'] = queryset.filter(start_datetime__gte=now)
        context['past_events'] = queryset.filter(start_datetime__lt=now)
        
        # Добавляем остальные данные в контекст
        context['categories'] = EventCategory.objects.all()
        context['selected_date'] = self.request.GET.get('selected-date', '')
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_relevance'] = self.request.GET.get('relevance')
        context['per_page'] = self.get_paginate_by(queryset)
        context['now'] = now
        
        return context 