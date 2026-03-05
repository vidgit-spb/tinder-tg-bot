# 🚀 Пошаговая инструкция деплоя с автообновлением

## 📋 Что вы получите:
- ✅ Бот работает 24/7 бесплатно
- ✅ Автоматическое обновление при изменениях
- ✅ Мгновенное тестирование после пуша в GitHub
- ✅ Логи и мониторинг

---

## 🎯 ЧАСТЬ 1: Подготовка GitHub репозитория

### Шаг 1: Инициализация Git

Откройте терминал и выполните:

```bash
cd /Users/macbookprom1/CascadeProjects/tinder-tg-bot

# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Tinder-like Telegram bot"
```

### Шаг 2: Создание репозитория на GitHub

1. Откройте https://github.com
2. Нажмите **"New repository"** (зелёная кнопка)
3. Заполните:
   - **Repository name:** `tinder-tg-bot`
   - **Description:** `Tinder-like dating bot for Telegram`
   - **Visibility:** Private (чтобы токен был скрыт)
4. **НЕ** ставьте галочки на "Add README" или ".gitignore"
5. Нажмите **"Create repository"**

### Шаг 3: Подключение к GitHub

GitHub покажет команды, выполните их:

```bash
# Замените YOUR_USERNAME на ваш GitHub username
git remote add origin https://github.com/YOUR_USERNAME/tinder-tg-bot.git
git branch -M main
git push -u origin main
```

**Пример:**
```bash
git remote add origin https://github.com/ivan123/tinder-tg-bot.git
git branch -M main
git push -u origin main
```

Введите ваш GitHub username и токен (или пароль).

---

## 🚂 ЧАСТЬ 2: Деплой на Railway.app

### Шаг 1: Регистрация на Railway

1. Откройте https://railway.app
2. Нажмите **"Login"**
3. Выберите **"Login with GitHub"**
4. Авторизуйте Railway доступ к вашему GitHub

### Шаг 2: Создание проекта

1. На главной странице Railway нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Найдите и выберите репозиторий **`tinder-tg-bot`**
4. Railway автоматически начнёт деплой

### Шаг 3: Настройка переменных окружения

**ВАЖНО:** Не храните токен в коде на GitHub!

1. В Railway откройте ваш проект
2. Перейдите на вкладку **"Variables"**
3. Нажмите **"New Variable"**
4. Добавьте:
   ```
   BOT_TOKEN = 8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c
   ```
5. Нажмите **"Add"**

### Шаг 4: Проверка деплоя

1. Перейдите на вкладку **"Deployments"**
2. Дождитесь статуса **"Success"** (зелёная галочка)
3. Откройте вкладку **"Logs"** чтобы увидеть:
   ```
   🤖 Bot is running!
   ✅ Bot started successfully!
   ```

---

## 🔄 ЧАСТЬ 3: Автоматическое обновление

### Как это работает:

```
Вы меняете код → git push → Railway автоматически деплоит → Бот обновлён!
```

### Пример: Изменение приветственного сообщения

1. **Откройте `config.py`**
2. **Измените:**
   ```python
   WELCOME_MESSAGE = "Привет! Найди свою любовь! 💕"
   ```
3. **Сохраните и запушьте:**
   ```bash
   git add config.py
   git commit -m "Update welcome message"
   git push
   ```
4. **Railway автоматически:**
   - Обнаружит изменения
   - Пересоберёт проект
   - Перезапустит бота
   - Через 30-60 секунд бот обновлён!

### Проверка обновления:

1. Откройте Railway → **Deployments**
2. Увидите новый деплой с вашим коммитом
3. Дождитесь **"Success"**
4. Проверьте в Telegram - изменения применены!

---

## 🔐 ЧАСТЬ 4: Безопасность токена

### Проблема: Токен в config.py попадёт на GitHub!

### Решение: Использовать переменные окружения

#### Шаг 1: Обновите config.py

Замените строку с токеном:

```python
import os

# Используем переменную окружения, если есть, иначе значение из файла
BOT_TOKEN = os.getenv('BOT_TOKEN', '8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c')
```

#### Шаг 2: Создайте .env для локальной разработки

Создайте файл `.env`:
```
BOT_TOKEN=8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c
```

#### Шаг 3: Обновите .gitignore

Убедитесь что `.env` в `.gitignore`:
```
.env
*.db
```

#### Шаг 4: Запуск локально с .env

Установите python-dotenv:
```bash
pip install python-dotenv
```

Добавьте в начало `bot.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

Теперь:
- **Локально:** токен берётся из `.env`
- **На Railway:** токен берётся из Variables
- **GitHub:** токен не попадает в репозиторий!

---

## 📊 ЧАСТЬ 5: Мониторинг и логи

### Просмотр логов в реальном времени:

1. Railway → ваш проект → вкладка **"Logs"**
2. Увидите все действия пользователей:
   ```
   User 123456 started registration
   User 123456 liked user 789012
   Match created between 123456 and 789012
   ```

### Проверка работы бота:

```bash
# Локально проверить статус
curl https://api.telegram.org/bot8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c/getMe
```

---

## 🔄 ЧАСТЬ 6: Рабочий процесс разработки

### Типичный цикл обновления:

```bash
# 1. Внесите изменения в код
nano config.py  # или любой редактор

# 2. Тестируйте локально
python3 bot.py
# Протестируйте в Telegram

# 3. Остановите локальный бот
Ctrl+C

# 4. Закоммитьте изменения
git add .
git commit -m "Add new feature: XYZ"

# 5. Запушьте на GitHub
git push

# 6. Railway автоматически задеплоит
# Ждите 30-60 секунд

# 7. Тестируйте на продакшене
# Откройте бота в Telegram
```

### Быстрые команды:

```bash
# Статус изменений
git status

# Посмотреть историю
git log --oneline

# Откатить последний коммит (если что-то сломалось)
git revert HEAD
git push

# Посмотреть разницу перед коммитом
git diff
```

---

## 🐛 ЧАСТЬ 7: Отладка проблем

### Бот не отвечает после деплоя:

1. **Проверьте логи в Railway:**
   - Logs → ищите ошибки красным цветом

2. **Проверьте переменные:**
   - Variables → убедитесь что `BOT_TOKEN` установлен

3. **Проверьте статус деплоя:**
   - Deployments → должен быть "Success"

### База данных сбросилась:

**Проблема:** Railway использует эфемерное хранилище

**Решение:** Используйте Railway Volumes или PostgreSQL

```bash
# В Railway добавьте Volume:
# Settings → Volumes → Add Volume
# Mount path: /app/data
```

Обновите `config.py`:
```python
DATABASE_PATH = "/app/data/dating_bot.db"
```

### Изменения не применяются:

1. Проверьте что закоммитили:
   ```bash
   git status
   ```

2. Проверьте что запушили:
   ```bash
   git log origin/main..main
   # Если есть коммиты - нужен push
   ```

3. Принудительный редеплой в Railway:
   - Deployments → три точки → "Redeploy"

---

## 💰 ЧАСТЬ 8: Лимиты бесплатного тарифа

### Railway.app Free Tier:

- **$5 кредитов в месяц**
- **~500 часов работы**
- **Достаточно для:**
  - 100-200 активных пользователей
  - Тысячи сообщений в день
  - Постоянная работа 24/7

### Если кредиты закончились:

**Вариант 1:** Render.com (750 часов бесплатно)
**Вариант 2:** Fly.io (3 VM бесплатно)
**Вариант 3:** VPS за $3-5/месяц (DigitalOcean, Hetzner)

---

## 📱 ЧАСТЬ 9: Тестирование после деплоя

### Чек-лист тестирования:

- [ ] Бот отвечает на `/start`
- [ ] Регистрация работает
- [ ] Можно загрузить фото
- [ ] Свайпинг показывает профили
- [ ] Лайки сохраняются
- [ ] Матчинг работает
- [ ] Чат между матчами работает
- [ ] Уведомления приходят
- [ ] Оплата Stars работает (только на проде)

### Создайте тестовые аккаунты:

1. Используйте 2-3 разных Telegram аккаунта
2. Зарегистрируйте их в боте
3. Протестируйте взаимные лайки
4. Проверьте чат

---

## 🎯 ЧАСТЬ 10: Полезные команды

### Git команды:

```bash
# Посмотреть удалённый репозиторий
git remote -v

# Обновить с GitHub
git pull

# Посмотреть ветки
git branch -a

# Создать новую ветку для экспериментов
git checkout -b feature-new-design
git push -u origin feature-new-design
```

### Railway CLI (опционально):

```bash
# Установка
npm i -g @railway/cli

# Логин
railway login

# Просмотр логов
railway logs

# Переменные
railway variables
```

---

## 📚 Краткая шпаргалка

### Обновить бота:

```bash
# 1. Измените код
# 2. Сохраните
git add .
git commit -m "описание изменений"
git push
# 3. Ждите 60 секунд - готово!
```

### Откатить изменения:

```bash
git revert HEAD
git push
```

### Посмотреть логи:

Railway.app → Logs

### Проверить статус:

Railway.app → Deployments

---

## ✅ Готово!

Теперь у вас:
- ✅ Бот на GitHub
- ✅ Автоматический деплой на Railway
- ✅ Обновления за 60 секунд
- ✅ Бесплатный хостинг 24/7
- ✅ Логи и мониторинг

**Любое изменение → git push → автоматически на продакшене!**

---

## 🆘 Нужна помощь?

- Railway документация: https://docs.railway.app
- Git туториал: https://git-scm.com/docs
- Telegram Bot API: https://core.telegram.org/bots/api
