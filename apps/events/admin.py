from django.contrib import admin
from .models import Event, EventCategory
from django.utils.html import format_html

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_display')
    search_fields = ('name',)
    
    @admin.display(description='Цвет')
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {};"></div>',
            obj.color
        )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'category',  # Используем category вместо event_type
        'get_datetime_range',
        'location',
        'organizer',
        'is_published'
    )
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published', 'start_datetime')
    search_fields = ('title', 'description', 'location')
    
    @admin.display(description='Время проведения')
    def get_datetime_range(self, obj):
        return f"{obj.start_datetime.strftime('%d.%m.%Y %H:%M')} - {obj.end_datetime.strftime('%H:%M')}"

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового объекта
            obj.organizer = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not change:  # Если это создание нового объекта
                instance.organizer = request.user
            instance.save()
        formset.save_m2m()