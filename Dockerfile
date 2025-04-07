# Dockerfile

# --- Этап 1: Сборка зависимостей ---
    FROM python:3.10-slim as builder

    # Устанавливаем переменные окружения
    ENV PYTHONUNBUFFERED 1
    ENV PYTHONDONTWRITEBYTECODE 1
    # Настройки Poetry
    ENV POETRY_VERSION=1.8.3
    ENV POETRY_HOME="/opt/poetry"
    ENV POETRY_NO_INTERACTION=1 \
        POETRY_VIRTUALENVS_CREATE=false \
        POETRY_CACHE_DIR='/var/cache/pypoetry' \
        PATH="$POETRY_HOME/bin:$PATH"
    
    # Устанавливаем системные зависимости для сборки (например, для psycopg2) и Poetry
    RUN apt-get update && apt-get install --no-install-recommends -y \
        # зависимости для psycopg2
        libpq-dev \
        build-essential \
        # curl для установки Poetry
        curl \
        # Очистка
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Устанавливаем Poetry
    RUN curl -sSL https://install.python-poetry.org | python3 -
    
    # Устанавливаем рабочую директорию
    WORKDIR /app
    
    # Копируем файлы зависимостей
    COPY pyproject.toml poetry.lock ./
    
    # Устанавливаем только production зависимости
    # --only main исключает dev зависимости
    RUN poetry install --no-root --only main
    
    
    # --- Этап 2: Финальный образ ---
    FROM python:3.10-slim as final
    
    # Устанавливаем переменные окружения
    ENV PYTHONUNBUFFERED 1
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV DJANGO_SETTINGS_MODULE=uibar_project_new.settings
    
    # Устанавливаем системные зависимости (только те, что нужны для работы, не для сборки)
    RUN apt-get update && apt-get install --no-install-recommends -y \
        # libpq5 нужна для работы psycopg2
        libpq5 \
        # Очистка
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Устанавливаем рабочую директорию
    WORKDIR /app
    
    # Копируем установленные зависимости из этапа сборки
    COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
    COPY --from=builder /app/pyproject.toml /app/poetry.lock ./
    
    # Копируем код приложения
    COPY . .
    
    # Собираем статические файлы
    # Убедись, что STATIC_ROOT определен в settings.py
    # Запускаем от имени poetry, чтобы он нашел python нужной версии, если нужно
    RUN python manage.py collectstatic --noinput
    
    # Создаем пользователя для запуска приложения (для безопасности)
    RUN useradd --system --create-home appuser
    USER appuser
    
    # Открываем порт, который будет слушать Gunicorn
    EXPOSE 8000
    
    # Команда для запуска приложения
    # Используем Gunicorn как WSGI сервер
    # Стало: Запускаем gunicorn как модуль Python
    CMD ["python", "-m", "gunicorn", "uibar_project_new.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--timeout=120"]