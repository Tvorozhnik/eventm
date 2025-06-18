from django import forms
from .models import Event
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category',
            'start_datetime', 'location', 
            'max_participants', 'status',
            'price', 'image'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'status': forms.Select(choices=Event.Status.choices),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['status'].choices = [
                (Event.Status.DRAFT, 'Черновик'),
                (Event.Status.MODERATION, 'На модерации')
            ]