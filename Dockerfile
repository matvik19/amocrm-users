FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /amocrm_users

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду запуска
CMD ["sh", "-c", "alembic upgrade head && gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]