# syntax=docker/dockerfile:1.5

FROM python:3.11-slim AS base

# Устанавливаем системные зависимости: wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*

# Задаём рабочую директорию
WORKDIR /usr/src/app

# Копируем файл зависимостей
COPY requirements.txt ./

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код и шаблоны
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]