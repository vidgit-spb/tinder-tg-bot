# ⚠️ Исправление конфликта ботов

## Проблема

```
telegram.error.Conflict: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

**Причина:** Два экземпляра бота работают одновременно с одним токеном.

---

## ✅ Решение

### Вариант 1: Остановить локальный бот

```bash
# Остановить все процессы bot.py
pkill -f "bot.py"

# Проверить что процессов нет
ps aux | grep "bot.py"
```

### Вариант 2: Остановить Railway бот

1. Откройте Railway.app
2. Перейдите в ваш проект
3. Settings → Pause Deployment

---

## 🎯 Правило: Один бот в один момент времени

### Для локальной разработки:
```bash
# 1. Остановите Railway
# Railway → Settings → Pause

# 2. Запустите локально
python3 bot.py
```

### Для продакшена:
```bash
# 1. Остановите локальный бот
pkill -f "bot.py"

# 2. Railway работает автоматически
# Ничего делать не нужно
```

---

## 🔄 Рабочий процесс

### Разработка и тестирование:

```bash
# 1. Остановите Railway (временно)
# Railway → Settings → Pause Deployment

# 2. Запустите локально
cd /Users/macbookprom1/CascadeProjects/tinder-tg-bot
python3 bot.py

# 3. Тестируйте в Telegram

# 4. Остановите локальный бот
Ctrl+C

# 5. Задеплойте на Railway
./deploy.sh

# 6. Возобновите Railway
# Railway → Settings → Resume Deployment
```

### Только продакшен:

```bash
# Просто деплойте - Railway работает автоматически
./deploy.sh

# Локальный бот НЕ запускайте!
```

---

## 🚨 Как проверить что бот не запущен локально

```bash
# Команда 1: Поиск процесса
ps aux | grep "bot.py"

# Если видите что-то вроде:
# user  12345  0.0  0.3  python3 bot.py
# Значит бот запущен!

# Остановите:
pkill -f "bot.py"

# Команда 2: Проверка портов (если используете webhook)
lsof -i :8080
```

---

## 📋 Чек-лист перед запуском

- [ ] Проверил что локальный бот остановлен (`ps aux | grep bot.py`)
- [ ] Проверил статус Railway (должен быть Running)
- [ ] Запускаю только ОДИН экземпляр
- [ ] Если тестирую локально - остановил Railway
- [ ] Если деплою - остановил локальный бот

---

## 🔧 Автоматическое решение

Добавьте в начало `bot.py`:

```python
import os
import sys

# Проверка что не запущен другой экземпляр
LOCK_FILE = '/tmp/dating_bot.lock'

if os.path.exists(LOCK_FILE):
    print("⚠️  Бот уже запущен!")
    print("Остановите другой экземпляр перед запуском нового.")
    sys.exit(1)

# Создаём lock файл
with open(LOCK_FILE, 'w') as f:
    f.write(str(os.getpid()))

# При завершении удаляем lock
import atexit
atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)
```

Это предотвратит запуск второго экземпляра на той же машине.

---

## 💡 Рекомендации

### ✅ ПРАВИЛЬНО:
- Локальная разработка → остановите Railway
- Продакшен → используйте только Railway
- Тестирование → один бот в один момент

### ❌ НЕПРАВИЛЬНО:
- Запускать локально И на Railway одновременно
- Забывать остановить локальный бот перед деплоем
- Использовать один токен для нескольких ботов

---

## 🎯 Текущая ситуация

**Сейчас:**
- Railway бот работает ✅
- Локальный бот был запущен ❌ (конфликт)

**Решение:**
```bash
# Остановите локальный
pkill -f "bot.py"

# Railway продолжит работать
# Бот заработает через 10-30 секунд
```

---

## 📞 Если проблема не решилась

1. **Перезапустите Railway:**
   - Railway → Deployments → три точки → Restart

2. **Проверьте логи:**
   - Railway → Logs
   - Должно быть: "Bot is running!"

3. **Проверьте токен:**
   - Railway → Variables → BOT_TOKEN
   - Должен совпадать с токеном из @BotFather

4. **Последний вариант - сбросьте webhook:**
   ```bash
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"
   ```

---

**Проблема решена! Теперь работает только Railway бот.** ✅
