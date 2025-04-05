# apartments/models.py
from django.db import models
from django.conf import settings # Для ссылки на модель User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError # Для валидации в модели
from django.utils import timezone # Для работы со временем

class Amenity(models.Model):
    """Модель для удобств (WiFi, Парковка и т.д.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название удобства")
    # slug = models.SlugField(max_length=100, unique=True, blank=True, null=True) # Можно добавить slug для URL или иконок
    # icon_class = models.CharField(max_length=50, blank=True, null=True) # Можно добавить класс иконки (напр., FontAwesome)

    class Meta:
         verbose_name = "Удобство"
         verbose_name_plural = "Удобства"
         ordering = ['name']

    def __str__(self):
         return self.name

class Apartment(models.Model):
    class ApartmentType(models.TextChoices):
        STUDIO = 'ST', 'Студия'
        ONE_ROOM = '1R', '1-комнатная'
        TWO_ROOM = '2R', '2-комнатная'
        THREE_ROOM = '3R', '3-комнатная'
        HOUSE = 'HO', 'Дом/Коттедж'
        OTHER = 'OT', 'Другое'
    # -----------------
    # Поля модели
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apartments')
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за ночь")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    city = models.CharField(max_length=100, verbose_name="Город")
    # --------------------------------------------------------

    apartment_type = models.CharField(
        max_length=2,
        choices=ApartmentType.choices,
        default=ApartmentType.ONE_ROOM, # Значение по умолчанию
        verbose_name="Тип жилья"
    )
    max_guests = models.PositiveSmallIntegerField(default=2, verbose_name="Макс. гостей")
    beds = models.PositiveSmallIntegerField(default=1, verbose_name="Кол-во кроватей")
  
    # Удобства
    amenities = models.ManyToManyField(Amenity, blank=True, verbose_name="Удобства")

    # Статус объявления
    is_active = models.BooleanField(default=True, verbose_name="Активно") # По умолчанию активно

    # Даты создания/обновления
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Сортировка по умолчанию - сначала новые
        verbose_name = "Квартира"
        verbose_name_plural = "Квартиры"

    def __str__(self):
        return f"{self.title} ({self.city})"
    
    
class Review(models.Model):
    """Модель для отзыва/комментария к квартире."""
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE, # Если квартира удалена, удаляем и отзыв
        related_name='reviews',   # Позволяет получить все отзывы: apartment.reviews.all()
        verbose_name="Квартира"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Если пользователь удален, удаляем и отзыв
        related_name='reviews',   # Позволяет получить все отзывы пользователя: user.reviews.all()
        verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    # Поле updated_at не так критично для отзыва, но можно добавить при желании
    updated_at = models.DateTimeField(auto_now=True)

    # Рейтинг 
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], # Оценка от 1 до 5
        verbose_name="Оценка",
        blank=True, null=True # Можно сделать необязательным
    )


    class Meta:
        ordering = ['-created_at'] # Сначала новые отзывы
        # Уникальность: один автор может оставить только один отзыв на одну квартиру
        unique_together = ('apartment', 'author')
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        # Возвращаем начало текста отзыва
        return f"Отзыв от {self.author.username} на {self.apartment.title}: {self.text[:30]}..."
    

# --- Модель Booking ---
class Booking(models.Model):
    """Модель для бронирования квартиры."""

    class BookingStatus(models.TextChoices):
        PENDING = 'PE', 'Ожидает подтверждения'
        CONFIRMED = 'CO', 'Подтверждено'
        CANCELLED = 'CA', 'Отменено'
        COMPLETED = 'CM', 'Завершено'

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Квартира"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Арендатор"
    )
    check_in_date = models.DateField(verbose_name="Дата заезда")
    check_out_date = models.DateField(verbose_name="Дата выезда")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость")
    status = models.CharField(
        max_length=2,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED,
        verbose_name="Статус бронирования"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def number_of_nights(self):
        if self.check_out_date and self.check_in_date:
            delta = self.check_out_date - self.check_in_date
            return delta.days
        return 0

    def clean(self):
        super().clean()
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise ValidationError("Дата выезда должна быть позже даты заезда.")
            # Проверку на прошлое можно делать и здесь, и в сериализаторе
            if self.check_in_date < timezone.now().date():
                 raise ValidationError("Дата заезда не может быть в прошлом.")
        # Проверка на пересечение дат остается в сериализаторе

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь {self.user.username} на {self.apartment.title} ({self.check_in_date} - {self.check_out_date})"

class ApartmentPhoto(models.Model):
    """Модель для хранения фотографий квартиры."""
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE, # При удалении квартиры удаляем и ее фото
        related_name='photos',    # Для доступа apartment.photos.all()
        verbose_name="Квартира"
    )
    # Поле для хранения самого изображения
    # upload_to='apartments/%Y/%m/%d/' - указывает, куда сохранять файлы
    # файлы будут сохраняться в MEDIA_ROOT/apartments/год/месяц/день/
    image = models.ImageField(upload_to='apartments/%Y/%m/%d/', verbose_name="Фото")
    # Можно добавить поле для описания фото (alt текст)
    # caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись")
    # Можно добавить поле для порядка сортировки фото
    # order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['pk'] # Или ['order'] если добавишь поле order
        verbose_name = "Фото квартиры"
        verbose_name_plural = "Фотографии квартир"

    def __str__(self):
        # Возвращаем путь к файлу или ID
        return f"Фото {self.id} для {self.apartment.title}"
