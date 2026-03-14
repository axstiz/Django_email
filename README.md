# 📧 Django Email — Внутренняя почта

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.3-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Приложение для обмена электронными письмами между пользователями на Django.

---

## 🚀 Быстрый старт

### 1. Клонирование

```bash
git clone <URL-репозитория>
cd Django_email
```

### 2. Создание виртуального окружения

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
cd my_email
copy .env.example .env      # Windows
# или
cp .env.example .env        # Linux/Mac
```

> **Примечание:** Для локальной разработки можно оставить значения в `.env` по умолчанию.

### 5. Создание базы данных

```bash
cd my_email
python manage.py migrate
```

### 6. Создание суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

📬 **Приложение доступно:** http://127.0.0.1:8000/

---

## 📋 Возможности

| Функция | Описание |
|---------|----------|
| ✉️ **Отправка писем** | Отправка писем между пользователями по username |
| 📁 **Папки** | Входящие, Отправленные, Черновики, Корзина |
| ✏️ **Черновики** | Сохранение и редактирование черновиков |
| 🔍 **Поиск** | Поиск по теме, тексту и отправителю |
| 📄 **Пагинация** | 10 писем на странице |
| 📬 **Статус прочтения** | Отметка о прочтении писем |
| 🎨 **Дизайн** | Адаптивный интерфейс в сиреневых тонах |
| 🔐 **Безопасность** | Защита от CSRF, валидация форм |
| 🧪 **Тесты** | 37 тестов покрывают основной функционал |

---

## 📂 Структура проекта

```
Django_email/
├── .gitignore              # Игнорируемые файлы
├── README.md               # Документация
├── requirements.txt        # Зависимости
└── my_email/
    ├── .env.example        # Пример переменных окружения
    ├── manage.py           # Утилита Django
    ├── app_email/          # Приложение почты
    │   ├── models.py       # Модель Email
    │   ├── views.py        # Представления
    │   ├── forms.py        # Формы
    │   ├── urls.py         # URL маршруты
    │   ├── admin.py        # Админ-панель
    │   ├── tests.py        # Тесты
    │   └── templates/      # HTML шаблоны
    ├── my_email/           # Настройки проекта
    │   ├── settings.py
    │   ├── urls.py
    │   └── ...
    └── static/
        └── css/
            └── styles.css  # Стили
```

---

## 🔧 Настройка

### Переменные окружения (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `SECRET_KEY` | Секретный ключ Django | `django-insecure-...` |
| `DEBUG` | Режим отладки | `True` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `EMAIL_BACKEND` | Бэкенд почты | `console.EmailBackend` |
| `EMAIL_HOST` | SMTP сервер | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP порт | `587` |
| `EMAIL_USE_TLS` | TLS | `True` |
| `EMAIL_HOST_USER` | Email для отправки | — |
| `EMAIL_HOST_PASSWORD` | Пароль приложения | — |

### Для продакшена

1. Установите `DEBUG = False`
2. Настройте `ALLOWED_HOSTS = yourdomain.com`
3. Используйте PostgreSQL/MySQL вместо SQLite
4. Настройте статические файлы: `python manage.py collectstatic`
5. Используйте gunicorn/uwsgi для запуска

---

## 📡 API

### Основные URL

| URL | Описание |
|-----|----------|
| `/` | Перенаправление на inbox или login |
| `/register/` | Регистрация |
| `/auth/login/` | Вход |
| `/auth/logout/` | Выход |
| `/<username>/` | Входящие |
| `/<username>/<folder>/` | Папка (inbox/sent/drafts/trash) |
| `/<username>/compose/` | Написать письмо |
| `/<username>/drafts/<slug>/edit/` | Редактировать черновик |
| `/<username>/email/<slug>/` | Просмотр письма |
| `/<username>/email/<slug>/move/` | Переместить |
| `/<username>/email/<slug>/delete/` | Удалить |

---

## 🧪 Тесты

```bash
cd my_email
python manage.py test app_email
```

**Покрытие:** 37 тестов
- ✅ Модели (Email)
- ✅ Представления (views)
- ✅ Формы (RegistrationForm, ComposeEmailForm)
- ✅ Черновики
- ✅ Корзина
- ✅ Поиск и пагинация

---

## 🗄️ Модель данных

### Email

```python
class Email(models.Model):
    sender      → ForeignKey(User)  # Отправитель
    recipient   → ForeignKey(User)  # Получатель
    subject     → CharField(200)    # Тема
    body        → TextField()       # Текст
    folder      → CharField()       # inbox/sent/drafts/trash
    timestamp   → DateTimeField()   # Дата
    read        → BooleanField()    # Прочитано
    slug        → SlugField()       # Уникальный ID
```

---

## 🎨 Дизайн

- **Основной цвет:** `#9b59b6` (сиреневый)
- **Ховер:** `#8e44ad` (тёмно-сиреневый)
- **Шрифт:** System fonts (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Адаптивность:** Мобильная версия включена

---

## 📝 Лицензия

MIT License — см. файл [LICENSE](LICENSE)

---

## 🤝 Вклад

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---
