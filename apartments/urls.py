# apartments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApartmentViewSet, AmenityViewSet, MyApartmentListView, ReviewViewSet # Импортируем наши ViewSet'ы

app_name = 'apartments' # Имя приложения для пространства имен URL (не обязательно для API, но хорошая практика)

# Создаем экземпляр роутера
router = DefaultRouter()

# Регистрируем ApartmentViewSet
# Префикс URL: /api/apartments/
# Базовое имя для имен URL: 'apartment' (-> 'apartment-list', 'apartment-detail')
router.register(r'apartments', ApartmentViewSet, basename='apartment')

# Регистрируем AmenityViewSet
# Префикс URL: /api/amenities/
# Базовое имя для имен URL: 'amenity' (-> 'amenity-list', 'amenity-detail')
router.register(r'amenities', AmenityViewSet, basename='amenity')
router.register(r'reviews', ReviewViewSet, basename='review')
# urlpatterns теперь содержат все URL-адреса, сгенерированные роутером
urlpatterns = [
    # Мы включаем сгенерированные роутером URL без дополнительного префикса здесь,
    # так как основной префикс 'api/' будет добавлен в главном urls.py проекта
    path('', include(router.urls)),
    path('my-apartments/', MyApartmentListView.as_view(), name='my-apartment-list'),
]