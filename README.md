# Team UFO Telegram-bot
![Bot_Logo](data/assets/simple_dimple_logo.png)

## Техническое задание

Цель проекта: Разработать Telegram-бота для автоматизации приема и обработки заявок от сотрудников к системным администраторам (например, заявки на установку ПО, настройку оборудования или починку техники).

Базовый функционал (Что должен уметь бот)
1. Интерфейс пользователя (Заявителя/сотрудника):
- Создание заявки: Бот должен запрашивать у пользователя описание проблемы (текстом или фото)
- Категоризация: Перед отправкой заявки пользователь выбирает категорию через inlline-кнопки (например: «Установка ПО», «Проблема с интернетом», «Не работает техника»).
- Статус тикета: Возможность нажать кнопку «Мои заявки» и посмотреть, на какой стадии находится проблема (В ожидании / В работе / Решено).

2. Интерфейс Системного администратора (Админ-панель в боте)
- Уведомления: При поступлении нового тикета бот присылает админу сообщение с деталями и кнопками действий.
- Управление статусами: Админ может нажать кнопку «Взять в работу» (заявителю приходит уведомление, что его проблемой занимаются) и «Закрыть тикет» (проблема решена).

3. База данных:
- Бот должен сохранять все тикеты в базу данных (SQLite или PostgreSQL), фиксируя Telegram ID пользователя, время создания заявки, суть проблемы и текущий статус.

## Технологический стек
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![Aiogram](https://img.shields.io/badge/aiogram-3.28.2-blue?style=for-the-badge&logo=telegram)  ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)  
**Язык программирования**: Python 3.14+
**Библиотека**: Aiogram 3.28.2
**База данных**: SQLite3

## Инструкция по запуску
1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/sibonk/team_ufo-telegram-bot
   cd team_ufo-telegram-bot
   ```
2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv .venv
   # Для Windows:
   .venv\Scripts\activate
   # Для Linux/macOS:
   source .venv/bin/activate
   ```
3. **Установите зависимости:**
   ```bash
   pip install aiogram==3.28.2
   ```
4. **Создайте файл конфигурации:**
   Создайте в корне проекта файл `.env` и добавьте туда ваш токен:
   ```env
   BOT_TOKEN=123token
   ```
5. **Запустите бота:**
   ```bash
   python main.py
   ```

## Структура проекта
```text
team_ufo-telegram-bot/
├── main.py
├── bd.db
├── .env
├── .gitignore
├── README.md
├── db/
│   └── models.py
├── handlers/
│   ├── app.py
│   ├── markup_keyboard.py
│   ├── admin/
│   │   ├── __init__.py
│   │   └── admin_handler.py
│   └── user/
│       ├── keyboard.py
│       ├── user_handler.py
│       └── user_handler_tickets.py
└── utils/
    └── config.py
```

# Демонстрация
![Bot_gif](data/assets/videoilus.gif)  