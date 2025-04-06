# Advertisement Service

## Описание

Тестовое задание выполнено в полном объеме.    
Реализованы все возможности пользовталя , администратора и доплнительный функционал

## Стек технологий

*   **Язык программирования:** Python 3.12+
*   **Фреймворк:** FastAPI 0.115.12+
*   **ORM:** SQLAlchemy 2.0.40+
*   **Асинхронный драйвер PostgreSQL:** asyncpg 0.30.0+
*   **Миграции базы данных:** Alembic 1.15.2+
*   **Веб-сервер:** Uvicorn 0.34.0+
*   **Аутентификация:** Passlib 1.7.4+, PyJWT 2.10.1+, bcrypt 4.3.0+
*   **Валидация данных:** Pydantic >=2.4.1,<2.11
*   **HTTP-клиент:** httpx 0.28.1+
*   **Тестирование:** pytest 8.3.5+, pytest-asyncio 0.26.0+
*   **Форматирование кода:** Black 25.1.0+

## Развертывание проекта

### Предварительные требования

*   Установленный Python 3.12+
*   Установленный Poetry (пакетный менеджер Python)

### Шаги

1.  **Клонируйте репозиторий:**

    ```bash
    git clone git@github.com:SemyonFalaleev/test_inlyit.git 
    ```

2.  **Установите зависимости с помощью Poetry:**

    ```bash
    poetry install
    ```

3.  **Настройте переменные окружения**

    Например оздайте файл `.env` в корне проекта и добавьте необходимые настройки. Пример:

    ```.env
        db_url=postgresql+asyncpg://<user>:<password>@<host>/<db_name>
        secret_key_jwt=<your_secret_key>
        algorithm_jwt=<your_algorithm>
        token_expires=<int>
        telegram_bot_token=<your_tg_bot_token>
        telegram_chat_id=<your_chat_id>
    ```

    *   `db_url`: URL для подключения к основной базе данных PostgreSQL.
    *   `secret_key_jwt`: Секретный ключ для подписи JWT токенов.
    *   `algoritm_jwt`: Алгоритм шифрования JWT.
    *   `token_expires`: Время жизни access токена в минутах.
    *   `telegram_bot_token`: Токен вашего Telegram бота.
    *   `telegram_chat_id`: ID чата Telegram, куда будут отправляться уведомления.

4.  **Примените миграции базы данных:**

    ```bash
    poetry run alembic upgrade head
    ```

    Убедитесь, что Alembic настроен правильно и файл `alembic.ini` указывает на вашу базу данных.

## Конфигурация

Проект использует файл `config.json` для конфигурации. Вы можете настроить следующие параметры:

*   `db_url`: URL для подключения к основной базе данных PostgreSQL.
*   `secret_key_jwt`: Секретный ключ для подписи JWT токенов.
*   `algoritm_jwt`: Алгоритм шифрования JWT (по умолчанию HS256).
*   `token_expires`: Время жизни access токена в минутах (по умолчанию 30).
*   `telegram_bot_token`: Токен вашего Telegram бота.
*   `telegram_chat_id`: ID чата Telegram, куда будут отправляться уведомления.

Измените файл `config.json` в соответствии с вашими потребностями.

## Запуск проекта

1.  **Запустите Uvicorn:**

    ```bash
    poetry run uvicorn main:app 
    ```

    *   `main:app`: Указывает на файл `main.py` и переменную `app` (экземпляр FastAPI).

### Документация API

FastAPI автоматически генерирует документацию API в формате OpenAPI (Swagger UI) и ReDoc. Вы можете получить доступ к документации по следующим URL:

*   Swagger UI: `http://localhost:8000/docs`

Замените `localhost:8000` на адрес и порт, на котором запущен ваш сервис.

### Примеры запросов

Примеры запросов можно найти в документации API.

## Тестирование

Перед началом тестирования, необходимо чтобы переменная окружения `db_url`    
содержала ссылку на пустую базу данных.

Для запуска тестов используйте следующую команду:

```bash
poetry run pytest