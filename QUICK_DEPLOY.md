# ⚡ Быстрый деплой за 5 минут

## 🎯 Краткая версия для опытных пользователей

### 1️⃣ GitHub (2 минуты)

```bash
cd /Users/macbookprom1/CascadeProjects/tinder-tg-bot

# Инициализация
git init
git add .
git commit -m "Initial commit"

# Создайте репозиторий на GitHub (Private!)
# Затем:
git remote add origin https://github.com/YOUR_USERNAME/tinder-tg-bot.git
git branch -M main
git push -u origin main
```

### 2️⃣ Railway.app (3 минуты)

1. https://railway.app → Login with GitHub
2. New Project → Deploy from GitHub repo → выберите `tinder-tg-bot`
3. Variables → Add Variable:
   ```
   BOT_TOKEN=8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c
   ```
4. Ждите деплой → Logs → проверьте "Bot is running!"

### 3️⃣ Обновления (30 секунд)

```bash
# Измените код
git add .
git commit -m "Update feature"
git push
# Railway автоматически задеплоит за 60 секунд!
```

---

## 📋 Полная инструкция

См. файл **DEPLOY_STEP_BY_STEP.md** для детальной инструкции.

---

## 🔐 Безопасность токена

**Важно:** Не коммитьте токен в GitHub!

### Вариант 1: Использовать переменные окружения (рекомендуется)

Токен уже настроен в `config.py` для использования переменных окружения:
```python
BOT_TOKEN = os.getenv('BOT_TOKEN', 'fallback_token')
```

На Railway просто добавьте переменную `BOT_TOKEN` и всё!

### Вариант 2: Удалить токен из config.py перед пушем

```bash
# Перед git push замените токен на:
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Затем на Railway добавьте реальный токен в Variables
```

---

## 🎯 Где что хранится

### Локально:
```
/Users/macbookprom1/CascadeProjects/tinder-tg-bot/
├── bot.py              # Код бота
├── config.py           # Настройки (токен здесь)
├── database.py         # База данных
├── dating_bot.db       # SQLite файл (НЕ коммитится)
└── .env                # Локальные переменные (НЕ коммитится)
```

### На GitHub:
```
Весь код БЕЗ:
- dating_bot.db (база данных)
- .env (переменные окружения)
- __pycache__/ (кэш Python)
```

### На Railway:
```
Код из GitHub + переменная BOT_TOKEN
```

### Фото пользователей:
```
НЕ хранятся нигде!
Telegram хранит фото → бот получает file_id → сохраняет только ID в БД
```

---

## 🔄 Рабочий процесс

```
Локальная разработка:
1. Измените код
2. python3 bot.py (тест локально)
3. Ctrl+C (остановка)

Деплой на продакшен:
4. git add .
5. git commit -m "описание"
6. git push
7. Railway автоматически деплоит (60 сек)
8. Тестируйте в Telegram
```

---

## 💡 Советы

- **Тестируйте локально** перед пушем
- **Коммиты часто** - маленькие изменения легче откатить
- **Осмысленные сообщения** коммитов
- **Проверяйте логи** в Railway после деплоя
- **Создайте ветку** для экспериментов: `git checkout -b test-feature`

---

## 🐛 Быстрое решение проблем

### Бот не запускается на Railway:
```
Railway → Logs → найдите ошибку
Railway → Variables → проверьте BOT_TOKEN
```

### Изменения не применились:
```bash
git status  # проверьте что закоммитили
git push    # проверьте что запушили
```

### Нужно откатить:
```bash
git revert HEAD
git push
```

---

## 📱 Контакты и помощь

- Полная инструкция: **DEPLOY_STEP_BY_STEP.md**
- Railway документация: https://docs.railway.app
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Готово! Ваш бот на продакшене за 5 минут! 🚀**
