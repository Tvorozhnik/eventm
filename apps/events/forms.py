from django import forms
from .models import Event
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category',
            'start_datetime', 'end_datetime',
            'location', 'max_participants', 'is_published'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        
        if start and end and start >= end:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала")
        
        return cleaned_data