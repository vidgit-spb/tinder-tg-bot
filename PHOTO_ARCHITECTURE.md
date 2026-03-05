# 📸 Архитектура хранения фотографий

## 🏗️ Как работает хранение фото в Telegram ботах

### **Важно: Фото НЕ хранятся на вашем сервере!**

---

## 📊 Архитектура

```
Пользователь → Отправляет фото → Telegram серверы
                                        ↓
                                  Сохраняют фото
                                        ↓
                                  Возвращают file_id
                                        ↓
Ваш бот ← Получает file_id ← Telegram API
    ↓
Сохраняет только file_id в SQLite
    ↓
База данных (dating_bot.db)
```

---

## 💾 Что хранится на вашем сервере

### В базе данных SQLite:
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    photo_id TEXT,  ← Только текстовый ID!
    ...
)
```

**Пример данных:**
```
photo_id = "AgACAgIAAxkBAAIBY2..."  (строка ~50-100 символов)
```

**Размер:** ~100 байт на пользователя (только текст)

---

## 🌐 Где реально хранятся фото

### Telegram CDN серверы:
- Фото загружаются на серверы Telegram
- Telegram хранит их бесплатно
- Доступны через file_id
- Не занимают место на вашем сервере
- Не тратят ваш трафик при показе

---

## 🔄 Как работает показ фото

### Когда бот показывает профиль:

```python
# 1. Бот берёт file_id из базы
user = db.get_user(user_id)
photo_id = user['photo_id']  # "AgACAgIAAxkBAAIBY2..."

# 2. Отправляет через Telegram API
await context.bot.send_photo(
    chat_id=viewer_id,
    photo=photo_id  # Telegram сам находит фото по ID
)

# 3. Telegram:
#    - Находит фото на своих серверах
#    - Отправляет напрямую пользователю
#    - Ваш сервер НЕ участвует в передаче
```

---

## 📈 Преимущества этой архитектуры

### ✅ Экономия места:
- 1000 пользователей = ~100 КБ (только ID)
- Без фото: 1000 пользователей = ~5 ГБ
- **Экономия: 50,000x**

### ✅ Экономия трафика:
- Фото передаются напрямую Telegram → Пользователь
- Ваш сервер не участвует
- Безлимитный трафик для фото

### ✅ Скорость:
- Telegram CDN очень быстрый
- Фото кэшируются
- Мгновенная загрузка

### ✅ Надёжность:
- Telegram гарантирует хранение
- Резервные копии автоматически
- Не потеряются при сбое вашего сервера

---

## 🔒 Безопасность

### Доступ к фото:
- file_id уникален для каждого бота
- Другие боты не могут получить фото по вашему file_id
- Фото доступны только через ваш бот

### Приватность:
- Telegram не показывает фото публично
- Доступ только через bot API
- Вы контролируете кому показывать

---

## 📊 Размеры и лимиты

### Telegram лимиты:
- **Максимальный размер фото:** 10 МБ (мы проверяем)
- **Формат:** JPG, PNG, WebP
- **Разрешение:** до 10000x10000 пикселей
- **Хранение:** бесплатно и бессрочно

### Наши лимиты:
```python
# В bot.py проверяем размер
file_size_mb = file.file_size / (1024 * 1024)
if file_size_mb > 10:
    await update.message.reply_text("❌ Фото слишком большое!")
```

---

## 🛠️ Техническая реализация

### 1. Загрузка фото (регистрация):
```python
# Пользователь отправляет фото
photo = update.message.photo[-1]  # Берём самое большое

# Получаем file_id
photo_id = photo.file_id  # "AgACAgIAAxkBAAIBY2..."

# Сохраняем в базу
data['photo_id'] = photo_id
db.create_user(..., photo_id=photo_id)
```

### 2. Показ фото (свайпинг):
```python
# Получаем кандидата
candidate = db.get_candidates(user_id)[0]

# Показываем фото
await context.bot.send_photo(
    chat_id=user_id,
    photo=candidate['photo_id'],  # Telegram найдёт фото
    caption=f"{candidate['name']}, {candidate['age']}"
)
```

### 3. Обновление фото:
```python
# Новое фото
new_photo_id = update.message.photo[-1].file_id

# Обновляем в базе
db.execute('UPDATE users SET photo_id = ? WHERE user_id = ?', 
           (new_photo_id, user_id))
```

---

## 🐛 Почему фото могут не загружаться

### Возможные причины:

#### 1. **Ошибка в обработке:**
```python
# Проблема: нет обработки ошибок
photo_id = photo.file_id  # Может упасть

# Решение: try-except
try:
    photo_id = photo.file_id
    data['photo_id'] = photo_id
except Exception as e:
    logger.error(f"Error: {e}")
    await update.message.reply_text("❌ Ошибка")
```

#### 2. **Состояние не установлено:**
```python
# Проблема: бот не знает что ждёт фото
state, data = db.get_user_state(user_id)
if state != STATES['REGISTRATION_PHOTO']:
    # Фото игнорируется!
```

#### 3. **Фото слишком большое:**
```python
# Проверка размера
if file_size_mb > 10:
    return  # Фото отклонено
```

#### 4. **Telegram API недоступен:**
```python
# Временная проблема Telegram
# Решение: повторить попытку
```

---

## ✅ Исправления в коде

### Добавлена полная обработка ошибок:

```python
elif state == STATES['REGISTRATION_PHOTO']:
    if update.message.photo:
        try:
            photo = update.message.photo[-1]
            
            # Проверка размера с обработкой ошибок
            try:
                file = await context.bot.get_file(photo.file_id)
                file_size_mb = file.file_size / (1024 * 1024)
                
                if file_size_mb > 10:
                    await update.message.reply_text("❌ Фото слишком большое!")
                    return
            except Exception as e:
                logger.error(f"Error checking file size: {e}")
                # Продолжаем даже если не удалось проверить
            
            # Сохраняем file_id
            photo_id = photo.file_id
            data['photo_id'] = photo_id
            db.set_user_state(user_id, STATES['REGISTRATION_CITY'], data)
            
            # Показываем города
            await update.message.reply_text("Perfect! Выберите город...")
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            await update.message.reply_text(
                "❌ Ошибка при обработке фото. Попробуйте ещё раз или /skip"
            )
```

---

## 📊 Статистика использования

### Пример на 1000 пользователей:

**Без Telegram (если бы хранили сами):**
- Средний размер фото: 5 МБ
- 1000 пользователей × 5 МБ = **5 ГБ**
- Трафик при показе: 5 МБ × просмотры
- Стоимость хранения: ~$0.10/ГБ/месяц = **$0.50/месяц**

**С Telegram (текущая архитектура):**
- Размер file_id: 100 байт
- 1000 пользователей × 100 байт = **100 КБ**
- Трафик при показе: **0** (Telegram CDN)
- Стоимость хранения: **$0** (бесплатно)

**Экономия:** 100% стоимости + безлимитный трафик

---

## 🎯 Итог

### Архитектура:
```
Telegram серверы (CDN)
    ↓ хранят фото
    ↓ бесплатно
    ↓ бессрочно
    
Ваш сервер (Railway)
    ↓ хранит только file_id
    ↓ ~100 байт на пользователя
    ↓ SQLite база данных
```

### Преимущества:
- ✅ Не занимает место на сервере
- ✅ Бесплатное хранение
- ✅ Быстрая загрузка (CDN)
- ✅ Надёжность (Telegram)
- ✅ Безлимитный трафик

**Фото хранятся на серверах Telegram, а не на вашем сервере!** 🎉
