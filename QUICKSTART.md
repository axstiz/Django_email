# ⚡ Быстрый старт

## Запуск за 5 команд

```bash
# 1. Создание виртуального окружения
python -m venv .venv && .venv\Scripts\activate  # Windows
# или: python3 -m venv .venv && source .venv/bin/activate  # Linux/Mac

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка .env
cd my_email && copy .env.example .env  # Windows
# или: cp .env.example .env  # Linux/Mac

# 4. Миграции
python manage.py migrate

# 5. Запуск
python manage.py runserver
```

🎉 **Готово!** Откройте http://127.0.0.1:8000/

---

## Создание первого пользователя

### Вариант 1: Через админку

```bash
python manage.py createsuperuser
```

Затем: http://127.0.0.1:8000/admin/

### Вариант 2: Через регистрацию

1. Откройте http://127.0.0.1:8000/register/
2. Введите username, email и пароль
3. Нажмите "Зарегистрироваться"

---

## Тестирование

```bash
cd my_email
python manage.py test app_email
```

✅ **37 тестов** должны пройти успешно.

---

## Очистка (если нужно начать заново)

```bash
# Удалить базу данных
del my_email\db.sqlite3  # Windows
# или: rm my_email/db.sqlite3  # Linux/Mac

# Создать заново
python manage.py migrate
```

---

## Частые проблемы

### ❌ Ошибка: "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

### ❌ Ошибка: "Port 8000 is in use"

```bash
# Запуск на другом порту
python manage.py runserver 8080
```

### ❌ Ошибка: "CSRF verification failed"

Очистите куки браузера или откройте в режиме инкогнито.

---

## Что дальше?

1. 📝 Зарегистрируйте 2-3 пользователя
2. ✉️ Отправьте письмо от одного к другому
3. 🗑️ Попробуйте переместить в корзину
4. ✏️ Создайте и отредактируйте черновик

**Удачи!** 🚀
