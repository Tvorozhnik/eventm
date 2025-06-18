from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Главная страница
    path('admin/', admin.site.urls),
    path('events/', include('apps.events.urls')),
    path('accounts/', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 