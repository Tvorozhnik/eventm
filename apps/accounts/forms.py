from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.core.validators import MinLengthValidator
from datetime import date
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label="Имя",
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Фамилия",
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'birth_date', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        age = (date.today() - birth_date).days // 365
        if age < 14:
            raise ValidationError("Регистрация доступна с 14 лет")
        return birth_date

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль',
            'autocomplete': 'current-password'
        })
    )

    def clean_username(self):
        email = self.cleaned_data.get('username')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email не найден')
        return email

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

class UserProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        label='Текущий пароль',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        })
    )
    
    new_password1 = forms.CharField(
        label='Новый пароль',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        })
    )
    
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль'
        })
    )

    delete_avatar = forms.BooleanField(
        label='Удалить фото профиля',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    bio = forms.CharField(
        label='О себе',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Расскажите о себе',
            'rows': 4
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Email обязательное поле
        self.fields['email'].required = True
        # Остальные поля не обязательные
        for field_name in ['first_name', 'last_name', 'bio', 'avatar']:
            self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        # Проверяем email
        email = cleaned_data.get('email')
        if not email:
            self.add_error('email', 'Email обязателен для заполнения')

        # Если пользователь хочет изменить пароль
        if new_password1 or new_password2 or current_password:
            if not current_password:
                self.add_error('current_password', 'Введите текущий пароль')
            if not new_password1:
                self.add_error('new_password1', 'Введите новый пароль')
            if not new_password2:
                self.add_error('new_password2', 'Подтвердите новый пароль')
            if new_password1 and new_password2 and new_password1 != new_password2:
                self.add_error('new_password2', 'Пароли не совпадают')
            if new_password1 and len(new_password1) < 8:
                self.add_error('new_password1', 'Пароль должен содержать минимум 8 символов')

        # Если отмечено удаление аватара, очищаем поле avatar
        if cleaned_data.get('delete_avatar'):
            cleaned_data['avatar'] = None

        return cleaned_data