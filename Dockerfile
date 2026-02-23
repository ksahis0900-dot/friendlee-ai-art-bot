# Используем легкий образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию логов (чтобы они сразу были видны в панели сервера)
ENV PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости для работы с изображениями
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем список зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Команда для запуска (мы обновим main.py, чтобы он работал в режиме сервера)
CMD ["python", "main.py", "--server"]
