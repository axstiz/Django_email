# Django Email — Приложение внутренней почты

Приложение для обмена электронными письмами между пользователями на Django.

## Возможности

- ✅ Регистрация и авторизация пользователей
- ✅ Отправка писем между пользователями (по username)
- ✅ Папки: Входящие, Отправленные, Черновики, Корзина
- ✅ Отметка о прочтении писем
- ✅ Перемещение писем между папками
- ✅ Удаление писем
- ✅ Поиск по письмам (тема, текст, отправитель)
- ✅ Пагинация списков писем
- ✅ Адаптивный дизайн
- ✅ Админ-панель для управления письмами
- ✅ Полное покрытие тестами

## Установка

### 1. Клонирование и установка зависимостей

```bash
cd Django_email
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте параметры:

```bash
cp my_email/.env.example my_email/.env
```

### 3. Применение миграций

```bash
cd my_email
python manage.py migrate
```

### 4. Запуск сервера

```bash
python manage.py runserver
```

Приложение доступно по адресу: http://127.0.0.1:8000/

## Запуск тестов

```bash
cd my_email
python manage.py test app_email
```

## Структура проекта

```
Django_email/
├── requirements.txt          # Зависимости проекта
├── .gitignore               # Игнорируемые файлы Git
└── my_email/                # Основной проект Django
    ├── .env                 # Переменные окружения (не в Git)
    ├── .env.example         # Пример переменных окружения
    ├── manage.py            # Утилита управления Django
    ├── db.sqlite3           # База данных SQLite
    ├── static/              # Статические файлы (CSS)
    │   └── css/
    │       └── styles.css   # Основные стили
    ├── my_email/            # Настройки проекта
    │   ├── settings.py      # Настройки Django
    │   ├── urls.py          # Корневые URL
    │   ├── wsgi.py          # WSGI конфигурация
    │   └── asgi.py          # ASGI конфигурация
    └── app_email/           # Приложение почты
        ├── models.py        # Модель Email
        ├── views.py         # Представления
        ├── forms.py         # Формы
        ├── urls.py          # URL приложения
        ├── admin.py         # Настройки админки
        ├── tests.py         # Тесты
        └── templates/
            ├── base.html    # Базовый шаблон
            ├── email/       # Шаблоны писем
            │   ├── inbox.html
            │   ├── list.html
            │   ├── detail.html
            │   ├── compose.html
            │   └── ...
            └── registration/ # Шаблоны аутентификации
                ├── login.html
                └── register.html
```

## Модель данных

### Email

| Поле | Тип | Описание |
|------|-----|----------|
| sender | ForeignKey | Отправитель (User) |
| recipient | ForeignKey | Получатель (User) |
| subject | CharField | Тема письма |
| body | TextField | Текст письма |
| folder | CharField | Папка (inbox/sent/drafts/trash) |
| timestamp | DateTimeField | Дата отправки |
| read | BooleanField | Прочитано ли |
| slug | SlugField | Уникальный идентификатор |

## API

### Основные URL

| URL | Описание |
|-----|----------|
| `/` | Перенаправление на inbox или login |
| `/register/` | Регистрация нового пользователя |
| `/auth/login/` | Вход в систему |
| `/auth/logout/` | Выход из системы |
| `/<username>/` | Входящие письма |
| `/<username>/<folder>/` | Письма в папке |
| `/<username>/compose/` | Написать письмо |
| `/<username>/email/<slug>/` | Просмотр письма |
| `/<username>/email/<slug>/move/` | Переместить письмо |
| `/<username>/email/<slug>/delete/` | Удалить письмо |

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `SECRET_KEY` | Секретный ключ Django | `your-secret-key` |
| `DEBUG` | Режим отладки | `True` / `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `EMAIL_BACKEND` | Бэкенд почты | `django.core.mail.backends.console.EmailBackend` |
| `EMAIL_HOST` | SMTP сервер | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP порт | `587` |
| `EMAIL_HOST_USER` | Пользователь SMTP | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Пароль SMTP | `your-password` |

## Требования

- Python 3.10+
- Django 6.0.3
- python-dotenv 1.2.2

## Лицензия

MIT
