# apartments/admin.py
from django.contrib import admin
from .models import Apartment, Amenity, Review # Импортируем наши модели

# Регистрируем модель Apartment для отображения в админке
@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'owner', 'price', 'is_active', 'created_at') # Колонки в списке
    list_filter = ('city', 'is_active', 'apartment_type') # Фильтры справа
    search_fields = ('title', 'description', 'city', 'address') # Поля для поиска
    list_editable = ('price', 'is_active') # Поля, которые можно редактировать прямо в списке
    date_hierarchy = 'created_at' # Навигация по дате создания

# Регистрируем модель Amenity для отображения в админке
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'id') # Показываем название и ID
    search_fields = ('name',)
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'apartment', 'author', 'text_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'apartment__title', 'author__username')
    autocomplete_fields = ['apartment'] 

    @admin.display(description='Текст отзыва')
    def text_preview(self, obj):
        # Функция для отображения короткой версии текста в списке
        from django.utils.html import escape
        return escape(obj.text[:50]) + '...' if len(obj.text) > 50 else escape(obj.text)
