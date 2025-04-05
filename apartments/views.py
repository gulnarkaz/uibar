# apartments/views.py
from rest_framework import viewsets, permissions, status, filters, generics, serializers # Добавляем filters и serializers
from rest_framework.response import Response # Добавляем Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend # Добавляем DjangoFilterBackend
from .models import Apartment, Amenity, Booking, Review, ApartmentPhoto # Импортируем модели
from .serializers import ApartmentSerializer, AmenitySerializer, ReviewSerializer, BookingSerializer, ApartmentPhotoSerializer # Импортируем сериализаторы
from .permissions import IsOwnerOrReadOnly, IsAuthorOrReadOnly # Импортируем пользовательские права доступа
from .gemini_utils import generate_apartment_description
from rest_framework.decorators import action
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
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # --- НОВОЕ ДЕЙСТВИЕ ДЛЯ ГЕНЕРАЦИИ ОПИСАНИЯ ---
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    # detail=True - действие для конкретного объекта (нужен /pk/)
    # methods=['post'] - будем вызывать через POST-запрос
    # permission_classes=[IsOwnerOrReadOnly] - только владелец может генерировать описание для своей квартиры
    def generate_description(self, request, pk=None):
        """
        Генерирует описание для квартиры с помощью Gemini API.
        """
        apartment = self.get_object() # Получаем объект квартиры по pk из URL

        # Проверяем права еще раз (хотя permission_classes уже должны были это сделать)
        self.check_object_permissions(request, apartment)

        # Вызываем нашу функцию-помощник
        description = generate_apartment_description(apartment)

        if description:
            # Если описание сгенерировано, возвращаем его
            # Можно также сразу сохранить его в поле description квартиры:
            # apartment.description = description
            # apartment.save(update_fields=['description'])
            # Но пока просто вернем текст, чтобы пользователь мог его посмотреть/отредактировать
            return Response({'description': description}, status=status.HTTP_200_OK)
        else:
            # Если произошла ошибка при генерации
            return Response(
                {'error': 'Failed to generate description. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания и просмотра СВОИХ бронирований.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Только авторизованные

    # Разрешаем только нужные методы (GET для списка/деталей, POST для создания)
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """
        Пользователь видит только свои бронирования.
        """
        return Booking.objects.filter(user=self.request.user).select_related('apartment', 'user').order_by('-created_at')

    def get_serializer_context(self):
        """
        Передаем request в контекст сериализатора (нужно для serializer.create).
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
class ApartmentPhotoUploadView(generics.CreateAPIView):
    """
    Представление для загрузки одного фото для квартиры.
    Принимает POST запрос с 'image' (файл) и 'apartment' (ID квартиры).
    """
    queryset = ApartmentPhoto.objects.all()
    serializer_class = ApartmentPhotoSerializer
    permission_classes = [permissions.IsAuthenticated] # Только авторизованные могут загружать
    # Указываем парсеры для обработки данных формы (multipart/form-data)
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # Проверяем, является ли пользователь владельцем квартиры, к которой добавляется фото
        apartment_id = self.request.data.get('apartment')
        try:
            apartment = Apartment.objects.get(pk=apartment_id)
            if apartment.owner != self.request.user:
                # Можно вызывать PermissionDenied или ValidationError
                raise serializers.ValidationError("You can only add photos to your own apartments.")
            # Если все ок, сохраняем фото, связь с квартирой установится через validated_data
            serializer.save()
        except Apartment.DoesNotExist:
             raise serializers.ValidationError("Apartment not found.")
        # В сериализаторе нужно будет УБРАТЬ read_only=True для apartment
        # или передать apartment напрямую: serializer.save(apartment=apartment)

class ApartmentPhotoDestroyView(generics.DestroyAPIView):
    """
    Представление для удаления фото квартиры.
    """
    queryset = ApartmentPhoto.objects.all()
    serializer_class = ApartmentPhotoSerializer # Не особо нужен для DELETE, но требуется
    permission_classes = [permissions.IsAuthenticated] # Только авторизованные

    def get_object(self):
        # Получаем объект фото (как в стандартном DestroyAPIView)
        obj = super().get_object()
        # Проверяем, что пользователь является владельцем КВАРТИРЫ, к которой относится фото
        if obj.apartment.owner != self.request.user:
            # Генерируем ошибку прав доступа
            self.permission_denied(
                self.request, message="You can only delete photos from your own apartments."
            )
        return obj