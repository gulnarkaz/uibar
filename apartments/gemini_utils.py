# apartments/gemini_utils.py

import google.generativeai as genai
from django.conf import settings # Для доступа к ключу из настроек
import logging # Для логгирования ошибок

# Получаем логгер
logger = logging.getLogger(__name__)

# --- Конфигурируем Gemini API ---
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Выбираем модель (flash - быстрая и недорогая, pro - более мощная)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        logger.info("Gemini API configured successfully.")
    else:
        model = None
        logger.warning("GEMINI_API_KEY not found in settings. Description generation disabled.")
except Exception as e:
    model = None
    logger.error(f"Error configuring Gemini API: {e}", exc_info=True)
# -----------------------------

def format_apartment_data_for_prompt(apartment):
    """Форматирует данные квартиры для вставки в промпт."""
    amenity_names = [amenity.name for amenity in apartment.amenities.all()]
    amenities_str = ", ".join(amenity_names) if amenity_names else "не указаны"

    data_str = (
        f"- Город: {apartment.city}\n"
        f"- Адрес: {apartment.address}\n"
        f"- Тип жилья: {apartment.get_apartment_type_display()}\n" # Используем display-метод для читаемого названия
        f"- Макс. гостей: {apartment.max_guests}\n"
        f"- Кроватей: {apartment.beds}\n"
        f"- Цена за ночь: {apartment.price} KZT\n"
        f"- Удобства: {amenities_str}"
    )
    return data_str

def generate_apartment_description(apartment):
    """
    Генерирует описание для объекта квартиры, используя Gemini API.
    Возвращает сгенерированный текст или None в случае ошибки.
    """
    if not model:
        logger.warning("Gemini model not configured. Cannot generate description.")
        return None # Возвращаем None, если модель не настроена

    # Форматируем данные для промпта
    apartment_data = format_apartment_data_for_prompt(apartment)

    # Составляем промпт
    prompt = (
        "Ты - копирайтер, специализирующийся на объявлениях об аренде жилья. "
        "Напиши привлекательное, дружелюбное и информативное описание для сдачи квартиры посуточно, то есть на короткий срок для туристов (примерно 50-100 слов), "
        "основываясь на следующих характеристиках:\n"
        f"{apartment_data}\n\n"
        "Описание должно быть на русском языке. Избегай избитых фраз. Подчеркни ключевые преимущества. "
        "Не включай цену или адрес в текст описания."
    )

    logger.debug(f"Generating description for apartment {apartment.id} with prompt:\n{prompt}")

    try:
        # Отправляем запрос к API
        response = model.generate_content(prompt)
        # Извлекаем текст из ответа
        generated_text = response.text
        logger.info(f"Successfully generated description for apartment {apartment.id}")
        return generated_text
    except Exception as e:
        # Логгируем ошибку, если что-то пошло не так с API
        logger.error(f"Error generating description for apartment {apartment.id}: {e}", exc_info=True)
        return None # Возвращаем None в случае ошибки