# auth_app/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Представление для регистрации нового пользователя.
    Использует RegisterSerializer для валидации и создания.
    Доступно всем (PermissionAllowAny).
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,) # Разрешаем доступ всем
    serializer_class = RegisterSerializer

# --- Представления для получения и обновления токенов ---
# Мы будем использовать стандартные представления из Simple JWT,
# их не нужно писать самим, только прописать в urls.py.
# Это TokenObtainPairView и TokenRefreshView.

# Можно добавить представление для получения информации о текущем пользователе:
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Представление для получения данных о текущем аутентифицированном пользователе.
    Использует UserSerializer для отображения.
    Доступно только аутентифицированным пользователям (IsAuthenticated).
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        # Возвращает объект текущего пользователя, который прикреплен к запросу
        return self.request.user