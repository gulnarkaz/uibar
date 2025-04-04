# auth_app/urls.py
from django.urls import path
from .views import RegisterView, CurrentUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # Представление для получения пары токенов (access, refresh)
    TokenRefreshView,  # Представление для обновления access токена с помощью refresh токена
)

app_name = 'auth_app' # Имя приложения для пространства имен URL

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'), # URL для регистрации
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # URL для получения токенов (логин)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # URL для обновления access токена
    path('me/', CurrentUserView.as_view(), name='current_user'), # URL для получения данных о текущем пользователе
]               