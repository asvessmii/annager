# Telegram Bot for Anna Hertz

## Описание

Этот Telegram бот разработан для Анны Герц, натуропата, помогающего женщинам становиться здоровыми и стройными. Бот предоставляет информацию о питании, теле и сознании, а также включает интерактивный тест для определения гормонального состояния и подбора рациона.

## Функционал

### Пользовательская часть

*   **Приветствие:** При первом запуске бот отправляет приветственное сообщение с изображением и информацией об Анне Герц.
*   **Подписка на канал:** Предлагает пользователю подписаться на Telegram-канал Анны Герц с полезной информацией.
*   **Проверка подписки:** Кнопка для проверки подписки на канал (в текущей реализации всегда возвращает положительный результат).
*   **Тест:** Короткий тест из 5 вопросов для определения гормонального состояния и подбора рациона. После прохождения теста пользователь получает результат и адаптированный рацион.

### Админ-панель

Доступ к админ-панели осуществляется по команде `/admin` (доступно только для ADMIN_ID, указанного в `bot.py`).

*   **Пользователи:** Просмотр списка всех пользователей бота с их ID, количеством набранных баллов в тесте и итоговым результатом (если тест пройден).
*   **Сообщения:** Просмотр списка всех сообщений бота. Возможность редактирования текста существующих сообщений.

## Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
    cd <НАЗВАНИЕ_ПАПКИ_РЕПОЗИТООРЯ>
    ```

2.  **Установите зависимости:**
    ```bash
    pip install python-telegram-bot
    ```

3.  **Настройте бота:**
    Откройте файл `bot.py` и замените следующие значения:
    *   `BOT_TOKEN`: Ваш токен Telegram бота, полученный от BotFather.
    *   `ADMIN_ID`: Ваш Telegram ID (числовой), чтобы получить доступ к админ-панели.

4.  **Запустите бота:**
    ```bash
    python3 bot.py
    ```

Бот начнет работу и будет доступен в Telegram.

## Структура проекта

*   `bot.py`: Основной файл бота, содержащий логику обработки команд, сообщений и взаимодействий с пользователем.
*   `db.py`: Модуль для работы с базой данных SQLite. Содержит функции для инициализации БД, сохранения и извлечения данных пользователей, сообщений и кнопок.
*   `bot_data.db`: Файл базы данных SQLite (будет создан автоматически при первом запуске).
*   `pasted_content.txt`: Исходное техническое задание.
*   `image.png`: Изображение, используемое в первом сообщении бота.

## Используемые технологии

*   Python 3
*   `python-telegram-bot` (библиотека для работы с Telegram Bot API)
*   SQLite (для хранения данных)

## Дальнейшие улучшения

*   Расширение функционала админ-панели (добавление/удаление сообщений, управление кнопками, загрузка изображений).
*   Реализация полноценной проверки подписки на канал.
*   Добавление более сложных сценариев взаимодействия с пользователем.
*   Интеграция платежной системы (если потребуется).


