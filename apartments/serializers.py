# apartments/serializers.py
from rest_framework import serializers
from .models import Apartment, Booking, Amenity, Review, ApartmentPhoto # Импортируем обе модели и Review
from auth_app.serializers import UserSerializer # Импортируем UserSerializer для владельца
from django.utils import timezone

class ApartmentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentPhoto
        fields = ['id', 'image', 'apartment'] # Добавим 'apartment' для ассоциации
        read_only_fields = ['id']
        #используем PrimaryKeyRelatedField.
        extra_kwargs = {
              'apartment': {'write_only': True, 'required': True}
        }
# --- Сериализатор для Удобств ---
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name'] # Определяем, какие поля показывать для Amenity

# --- Сериализатор для Квартир ---
class ApartmentSerializer(serializers.ModelSerializer):
    # Для чтения: Показываем полные данные владельца
    owner = UserSerializer(read_only=True)
    # Для чтения: Показываем полные данные удобств (список объектов)
    amenities = AmenitySerializer(many=True, read_only=True)

    # Для записи: Принимаем список ID удобств
    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,            # Только для записи (не будет в ответе JSON)
        queryset=Amenity.objects.all(), # Для проверки, что такие ID существуют
        source='amenities',         # Указывает, что данные нужно сохранить в поле 'amenities' модели
        required=False              # Не обязательно передавать при создании/обновлении
    )
    photos = ApartmentPhotoSerializer(many=True, read_only=True) # read_only, т.к. фото загружаются отдельно
    class Meta:
        model = Apartment
        # Включаем все нужные поля модели и поле 'amenity_ids' для записи
        fields = [
            'id',
            'owner',            # Объект владельца (только чтение)
            'title',
            'description',
            'price',
            'address',
            'city',
            'apartment_type',   # Новое поле
            'max_guests',       # Новое поле
            'beds',             # Новое поле
            'amenities',        # Список объектов удобств (только чтение)
            'amenity_ids',  # Список ID удобств (только запись)
            'photos',           # Список объектов фото (только чтение)
            'is_active',
            'created_at',
            'updated_at',
        ]
        # Явно указываем поля только для чтения
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'photos']

    # Валидация цены (остается как была)
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    # Отображаем автора с помощью его сериализатора (только чтение)
    author = UserSerializer(read_only=True)
    # При создании отзыва нам нужно будет передать ID квартиры.
    # Поэтому поле apartment делаем НЕ read_only, а ссылкой на первичный ключ.
    apartment = serializers.PrimaryKeyRelatedField(
        queryset=Apartment.objects.all() # Для валидации существования квартиры
        # read_only=False # По умолчанию read_only=False для PrimaryKeyRelatedField
    )

    class Meta:
        model = Review
        fields = [
            'id',
            'apartment', # ID квартиры (при создании/обновлении), объект при чтении (нужно настроить)
            'author',    # Объект автора (только чтение)
            'text',
            'created_at',
            # 'rating', # Если добавили поле рейтинга
        ]
        # Автор назначается автоматически, дата создания тоже
        read_only_fields = ['id', 'author', 'created_at']


    def validate(self, data):
        """
        Проверка, что пользователь еще не оставлял отзыв на эту квартиру.
        """
        # Получаем пользователя из контекста запроса
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
             # На всякий случай, если контекст не передан
             return data

        author = request.user
        apartment = data.get('apartment')

        # Проверяем только при создании нового отзыва (instance is None)
        if self.instance is None and Review.objects.filter(apartment=apartment, author=author).exists():
            raise serializers.ValidationError("You have already reviewed this apartment.")
        return data

class LimitedApartmentSerializer(serializers.ModelSerializer):
    # Можно показать только ID владельца или его username
    owner = serializers.ReadOnlyField(source='owner.username') # Показываем username владельца

    class Meta:
        model = Apartment
        # Указываем только нужные поля
        fields = ('id', 'title', 'price', 'city', 'owner')
        
class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    apartment_details = ApartmentSerializer(source='apartment', read_only=True)
    apartment = serializers.PrimaryKeyRelatedField(
        queryset=Apartment.objects.filter(is_active=True),
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',             # Пользователь (read-only)
            'apartment',        # ID квартиры (write-only)
            'apartment_details',# Краткие данные квартиры (read-only) <--- ИЗМЕНЕНИЕ
            'check_in_date',
            'check_out_date',
            'number_of_nights', # Наше @property (read-only)
            'total_price',      # Цена (read-only, будет рассчитана)
            'status',           # Статус (read-only, будет установлен)
            'created_at'
        ]
        # Обновляем read_only_fields
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at', 'number_of_nights', 'apartment_details']

    # --- Метод validate (упрощенный, без проверки доступности) ---
    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        if check_in >= check_out:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда.")
        if check_in < timezone.now().date():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом.")
        # !!! Не забыть вернуть проверку доступности позже !!!
        return data

    # --- Метод create (без изменений) ---
    def create(self, validated_data):
        # ... (код метода create как был) ...
        apartment = validated_data.get('apartment')
        check_in = validated_data.get('check_in_date')
        check_out = validated_data.get('check_out_date')
        request = self.context.get('request')
        nights = (check_out - check_in).days
        if nights <= 0: raise serializers.ValidationError("Некорректное количество ночей.")
        total_price = nights * apartment.price
        booking = Booking.objects.create(
            user=request.user, apartment=apartment, check_in_date=check_in,
            check_out_date=check_out, total_price=total_price, status=Booking.BookingStatus.CONFIRMED
        )
        return booking

