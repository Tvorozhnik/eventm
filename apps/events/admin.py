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
    list_display = ('title', 'category', 'get_datetime', 'location', 'organizer', 'status')
    list_editable = ('status',)
    list_filter = ('status', 'category', 'start_datetime')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organizer=request.user)

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        return obj.organizer == request.user

    @admin.display(description='Дата и время')
    def get_datetime(self, obj):
        """Форматирует дату и время мероприятия"""
        return obj.start_datetime.strftime('%d.%m.%Y %H:%M')

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