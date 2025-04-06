# auth_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model # Получаем модель пользователя, указанную в settings.AUTH_USER_MODEL
from django.contrib.auth.password_validation import validate_password # Для валидации сложности пароля
from django.core import exceptions as django_exceptions

User = get_user_model() # Получаем нашу кастомную модель User

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе (без пароля)"""
    class Meta:
        model = User
        # Перечисляем поля, которые хотим видеть в API ответах
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        # Поля только для чтения (нельзя изменить через этот сериализатор напрямую)
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirm password")
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    city = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = User
        # Поля, которые принимаем при регистрации
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'city')
        # Поля, которые будут обязательными при регистрации
        extra_kwargs = {
            'first_name': {'required': False}, # Можно сделать необязательными
            'last_name': {'required': False},
            'email': {'required': True}, # Делаем email обязательным
            'username': {'required': True}, # Делаем username обязательным
            'phone': {'required': False}, # Можно сделать необязательными
            'city': {'required': False}, # Можно сделать необязательными
        }

    def validate_email(self, value):
        """Проверка на уникальность email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate(self, attrs):
        """
        Общая валидация данных:
        1. Проверка совпадения паролей.
        2. Валидация сложности пароля.
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        # 1. Проверка совпадения паролей
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})

        # Убираем подтверждение пароля, оно больше не нужно
        attrs.pop('password_confirm')

        # 2. Валидация сложности пароля стандартными валидаторами Django
        # Создаем временного пользователя для валидации, т.к. validate_password требует объект пользователя
        # Используем **attrs чтобы передать username, email и т.д., если они нужны валидаторам
        temp_user_data = {field: attrs.get(field) for field in User.REQUIRED_FIELDS}
        temp_user_data['email'] = attrs.get('email') # email часто используется в валидаторах
        temp_user_data['username'] = attrs.get('username')

        # Создаем объект User без сохранения в БД для валидации
        user = User(**temp_user_data)

        try:
            validate_password(password, user=user)
        except django_exceptions.ValidationError as e:
            # Поднимаем ошибку валидации DRF вместо Django
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs


    def create(self, validated_data):
        """
        Создание нового пользователя (альтернативный подход).
        Сначала создаем пользователя через create_user с основными полями,
        затем добавляем остальные поля и сохраняем.
        """
        # Извлекаем наши кастомные и необязательные поля из validated_data
        # Используем None как дефолтное значение, если поле не передано
        phone = validated_data.get('phone', None)
        city = validated_data.get('city', None)
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        # Создаем пользователя, передавая только то, что точно ожидает create_user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Теперь устанавливаем остальные поля для созданного объекта user
        user.first_name = first_name
        user.last_name = last_name
        # Ensure the User model has a 'phone' field before assigning
        if hasattr(user, 'phone'):
            user.phone = phone
        # Ensure the User model has a 'city' field before assigning
        if hasattr(user, 'city'):
            user.city = city

        # Сохраняем изменения (добавленные поля)
        user.save() # <-- ВАЖНО: Сохраняем после добавления доп. полей

        return user