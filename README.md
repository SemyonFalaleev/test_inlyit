# Advertisement Service

## Описание

Тестовое задание выполнено в полном объеме.  
Реализованы все возможности пользователя, администратора и дополнительный функционал.

## Стек технологий

- Язык программирования: Python 3.12+
- Фреймворк: FastAPI 0.115.12+
- ORM: SQLAlchemy 2.0.40+
- Асинхронный драйвер PostgreSQL: asyncpg 0.30.0+
- Миграции базы данных: Alembic 1.15.2+
- Веб-сервер: Uvicorn 0.34.0+
- Аутентификация: Passlib 1.7.4+, PyJWT 2.10.1+, bcrypt 4.3.0+
- Валидация данных: Pydantic >=2.4.1,<2.11
- HTTP-клиент: httpx 0.28.1+
- Тестирование: pytest 8.3.5+, pytest-asyncio 0.26.0+
- Форматирование кода: Black 25.1.0+

## Развертывание проекта

### Вариант 1: Локальная установка (без Docker)

#### Предварительные требования
- Установленный Python 3.12+
- Установленный Poetry (пакетный менеджер Python)
- PostgreSQL 13+

#### Шаги
1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:SemyonFalaleev/test_inlyit.git
   cd test_inlyit
   ```

2. Установите зависимости:
   ```bash
   poetry install
   ```

3. Настройте переменные окружения (создайте `.env` файл):
   ```ini
   db_url=postgresql+asyncpg://user:password@localhost/db_name
   secret_key_jwt=your_secret_key
   algorithm_jwt=HS256
   token_expires=30
   telegram_bot_token=your_tg_bot_token
   telegram_chat_id=your_chat_id
   ```

4. Примените миграции:
   ```bash
   poetry run alembic upgrade head
   ```
5. Для корректной уведомлений в телеграм чат,     
   необходимо добавить бота в телеграм чат,    
   `id` которого прописанно в переменной окружения
   `telegram_chat_id`, и сделать его администратором.
   
6. Запустите сервер:
   ```bash
   poetry run uvicorn main:app --reload
   ```

### Вариант 2: Запуск через Docker

#### Предварительные требования
- Установленный Docker
- Установленный Docker Compose (рекомендуется)

#### Инструкция по сборке и запуску

1. Соберите образ:
   ```bash
   docker build -t advertisement-service .
   ```

2. Запустите контейнер (замените значения переменных окружения на свои):
   ```bash
   docker run -d -p 8000:8000 \
     -e db_url="postgresql+asyncpg://user:password@host/db_name" \
     -e secret_key_jwt="your_secret_key" \
     -e algorithm_jwt="HS256" \
     -e token_expires="30" \
     -e telegram_bot_token="your_tg_bot_token" \
     -e telegram_chat_id="your_chat_id" \
     --name ad_service advertisement-service
   ```

#### Альтернативно с Docker Compose

1. Создайте `docker-compose.yml`:
   ```yaml
   version: '3.8'

   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - db_url=postgresql+asyncpg://user:password@host/db_name
         - secret_key_jwt=your_secret_key
         - algorithm_jwt=HS256
         - token_expires=30
         - telegram_bot_token=your_tg_bot_token
         - telegram_chat_id=your_chat_id
       depends_on:
         - db

     db:
       image: postgres:13
       environment:
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
         POSTGRES_DB: db_name
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:
   ```

2. Запустите:
   ```bash
   docker-compose up -d
   ```
## Конфигурация

Проект использует переменные окружения для конфигурации. Основные параметры:

- `db_url`: URL для подключения к PostgreSQL
- `secret_key_jwt`: Секретный ключ для JWT
- `algorithm_jwt`: Алгоритм шифрования (по умолчанию HS256)
- `token_expires`: Время жизни токена в минутах (по умолчанию 30)
- `telegram_bot_token`: Токен Telegram бота
- `telegram_chat_id`: ID чата для уведомлений

## Документация API

После запуска сервера документация будет доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тестирование

Для запуска тестов:
```bash
poetry run pytest
```
Или через Docker:
```bash
docker exec ad_service pytest
```