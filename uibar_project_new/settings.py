"""
Django settings for uibar_project_new project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os  # Добавлен для getenv
from dotenv import load_dotenv # Добавлена функция для загрузки .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Загрузка переменных окружения из .env файла ---
# Ищем .env файл в корневой папке проекта (рядом с manage.py)
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Using default settings or environment variables.")
# -------------------------------------------------

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Заменяем на чтение из .env
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-needs-to-be-set-in-env') # Добавлен дефолтный ключ на случай отсутствия .env

# SECURITY WARNING: don't run with debug turned on in production!
# Заменяем на чтение из .env, преобразуя строку в Boolean
DEBUG = os.getenv('DEBUG', 'False') == 'True' # По умолчанию False, если не найдено в .env

# ALLOWED_HOSTS можно тоже вынести в .env при необходимости, особенно для продакшена
# Для локальной разработки текущий вариант допустим
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
# В продакшене: os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',

    # Наши приложения
    'auth_app',
    'apartments',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uibar_project_new.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'uibar_project_new.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# --- Настройки базы данных из .env ---
DB_NAME = os.getenv('DB_NAME', 'apartments_db') # Дефолтное имя, если нет в .env
DB_USER = os.getenv('DB_USER', 'apartment_user')
DB_PASSWORD = os.getenv('DB_PASSWORD') # Пароль обязателен, не ставим дефолт
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
# -------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Используем более общий/современный alias
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'url': os.getenv('DB_URL'),
        },
    }
}

# Проверка, установлен ли пароль БД (важно!)
if DATABASES['default']['PASSWORD'] is None and not DEBUG: # В режиме DEBUG можно допустить отсутствие пароля для локальной БД, но не на проде
    print("ERROR: Database password is not set in environment variables (.env file).")
    # В реальном приложении здесь может быть более строгая обработка ошибки


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us' # Или 'ru-ru', если предпочитаешь русский

TIME_ZONE = 'UTC' # Или твой часовой пояс, например, 'Asia/Almaty'

USE_I18N = True

USE_TZ = True # Важно оставить True для корректной работы с часовыми поясами в БД


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Понадобится для сбора статики на проде
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель пользователя
AUTH_USER_MODEL = 'auth_app.User'

# Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend', 
    )
}

# Настройки Simple JWT
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    
    # Разрешить обновление refresh токенов (когда старый refresh используется, выдается новый)
    "ROTATE_REFRESH_TOKENS": True,
    # Добавлять старый refresh токен в черный список после использования
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True, # Обновлять поле last_login пользователя при обновлении токена

    "ALGORITHM": "HS256", # Алгоритм подписи
    "SIGNING_KEY": SECRET_KEY, # Используем SECRET_KEY проекта (можно сгенерировать отдельный)
    "VERIFYING_KEY": None, # Обычно не требуется для HS256
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",), # Тип заголовка авторизации (Bearer <token>)
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION", # Имя заголовка в Django request.META
    "USER_ID_FIELD": "id", # Поле в модели User, которое будет в payload токена
    "USER_ID_CLAIM": "user_id", # Имя claim в payload токена для ID пользователя

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule', # Стандартное правило
}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# --- Опционально для работы за прокси (как на Render) ---
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# USE_X_FORWARDED_HOST = True
