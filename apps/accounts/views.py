from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.utils import timezone
import os

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем только 3 последних организованных мероприятия
        context['latest_organized_events'] = self.request.user.organized_events.all().order_by('-start_datetime')[:3]
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = self.request.user
        
        # Проверка текущего пароля и обновление пароля
        current_password = form.cleaned_data.get('current_password')
        new_password1 = form.cleaned_data.get('new_password1')
        
        if current_password:
            # Проверяем текущий пароль
            if not user.check_password(current_password):
                form.add_error('current_password', 'Неверный текущий пароль')
                return self.form_invalid(form)
            
            # Если пароль верный и новый пароль предоставлен, меняем пароль
            if new_password1:
                user.set_password(new_password1)
                # Сохраняем пользователя
                user.save()
                # Обновляем сессию, чтобы пользователь не вылетел
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(self.request, user)
                messages.success(self.request, 'Пароль успешно изменен!')

        # Обработка удаления аватара
        if form.cleaned_data.get('delete_avatar'):
            if user.avatar:
                try:
                    old_avatar = user.avatar.path
                    if os.path.exists(old_avatar):
                        os.remove(old_avatar)
                    user.avatar = None
                except Exception as e:
                    print(f"Ошибка при удалении аватара: {e}")

        # Обработка загрузки нового аватара
        if 'avatar' in form.changed_data and form.cleaned_data['avatar']:
            if user.avatar:
                try:
                    old_avatar = user.avatar.path
                    if os.path.exists(old_avatar):
                        os.remove(old_avatar)
                except Exception as e:
                    print(f"Ошибка при удалении старого аватара: {e}")

        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлен!')
        return response

class OrganizedEventsListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/organized_events_list.html'
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        return self.request.user.organized_events.all().order_by('-start_datetime')