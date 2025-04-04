# apartments/views.py
from rest_framework import viewsets, permissions, status, filters, generics, serializers # Добавляем filters и serializers
from rest_framework.response import Response # Добавляем Response
from django_filters.rest_framework import DjangoFilterBackend # Добавляем DjangoFilterBackend
from .models import Apartment, Amenity # Импортируем модели
from .serializers import ApartmentSerializer, AmenitySerializer # Импортируем сериализаторы
from .permissions import IsOwnerOrReadOnly # Импортируем пользовательские права доступа
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsAuthorOrReadOnly
# --- ViewSet для Удобств (Amenity) ---
# Создадим простой ViewSet только для чтения списка удобств,
# это может быть полезно для фронтенда, чтобы знать, какие удобства доступны.
class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра списка доступных удобств.
    Только чтение (list, retrieve).
    """
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny] # Разрешаем просмотр всем
    pagination_class = None # Отключаем пагинацию для удобств, их обычно не так много
# ------------------------------------


# --- ViewSet для Квартир (Apartment) ---
class ApartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования объявлений квартир.
    """
    # Используем prefetch_related для оптимизации запроса удобств (ManyToMany)
    # Используем select_related для оптимизации запроса владельца (ForeignKey)
    queryset = Apartment.objects.filter(is_active=True).select_related('owner').prefetch_related('amenities')
    serializer_class = ApartmentSerializer
    permission_classes = [IsOwnerOrReadOnly] # Читать могут все, создавать/изменять - авторизованные


    # Добавим фильтрацию по городу, комн и т.д. с помощью django-filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['city', 'apartment_type', 'max_guests', 'beds'] # Поля для фильтрации
    ordering_fields = ['price', 'created_at'] # Поля для сортировки
    ordering = ['-created_at'] # Сортировка по умолчанию
    # --------------------------------
    
class MyApartmentListView(generics.ListAPIView):
    """
    Представление для получения списка квартир,
    принадлежащих текущему аутентифицированному пользователю.
    Доступно только аутентифицированным пользователям.
    """
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated] # Только для авторизованных

    def get_queryset(self):
        """
        Возвращает queryset, отфильтрованный по текущему пользователю.
        Включает как активные, так и неактивные объявления пользователя.
        """
        user = self.request.user
        # Фильтруем квартиры по владельцу и оптимизируем запрос
        return Apartment.objects.filter(owner=user).select_related('owner').prefetch_related('amenities').order_by('-created_at') # Добавляем сортировку
# ---------------------------------------------------------------------
    def perform_create(self, serializer):
        """
        Автоматически устанавливаем владельца при создании объявления.
        """
        serializer.save(owner=self.request.user)
        
class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания, просмотра, изменения и удаления отзывов.
    """
    serializer_class = ReviewSerializer
    # Права: читать могут все, остальное - только автор
    permission_classes = [IsAuthorOrReadOnly]
    # Фильтрация: По умолчанию показываем все отзывы, но даем возможность
    # фильтровать по ID квартиры (?apartment=...)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['apartment'] # Разрешаем фильтрацию по полю apartment

    # Базовый queryset - все отзывы
    queryset = Review.objects.all().select_related('author', 'apartment') # Оптимизация

    def perform_create(self, serializer):
        """
        Назначаем автора отзыва при создании.
        """
        # Проверяем, что пользователь аутентифицирован (хотя IsAuthorOrReadOnly это тоже сделает)
        if not self.request.user.is_authenticated:
             raise serializers.ValidationError("Authentication required to post reviews.")
        serializer.save(author=self.request.user)
