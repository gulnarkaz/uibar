"""
URL configuration for uibar_project_new project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# uibar_project_new/urls.py
from django.contrib import admin
from django.urls import path, include # Не забудь добавить include
# --- Добавляем импорты для медиафайлов ---
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем URL-маршруты из приложения auth_app
    # Все URL из auth_app будут доступны по префиксу /api/auth/
    path('api/auth/', include('auth_app.urls', namespace='auth_app')),
   
    # Префикс /api/ будет добавлен ко всем URL из router (т.е. /api/apartments/ и /api/amenities/)
    path('api/', include('apartments.urls', namespace='apartments')),
]
# --- Добавляем раздачу медиафайлов в режиме DEBUG ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)