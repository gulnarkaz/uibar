# apartments/serializers.py
from rest_framework import serializers
from .models import Apartment, Amenity, Review # Импортируем обе модели и Review
from auth_app.serializers import UserSerializer # Импортируем UserSerializer для владельца

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
            'amenity_ids',      # Список ID удобств (только запись)
            'is_active',
            'created_at',
            'updated_at',
        ]
        # Явно указываем поля только для чтения
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

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

    # --- Опционально: Улучшение отображения apartment при чтении ---
    # Чтобы при GET запросе видеть не просто ID квартиры, а ее данные,
    # можно использовать depth или переопределить to_representation:
    # Либо в Meta:
    # depth = 1 # Показывает вложенные объекты на 1 уровень (Apartment и Author)

    # Либо так (более гибко):
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # Используем ApartmentSerializer для поля apartment, но только основные поля
    #     representation['apartment'] = ApartmentSerializer(instance.apartment, context=self.context, fields=('id', 'title', 'city')).data
    #     return representation
    # Для этого нужно будет импортировать или настроить ApartmentSerializer соответственно.
    # Пока оставим вывод ID квартиры для простоты.
    # --------------------------------------------------------------

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
