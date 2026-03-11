import logging
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, PreCheckoutQueryHandler
from database import Database
from config import *
from cities import get_city_keyboard, get_city_name, get_city_display
from admin import admin_command, admin_callback

# Bot version - increment to force Railway rebuild
BOT_VERSION = "2.2.0"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info(f"Starting bot version {BOT_VERSION}")

db = Database(DATABASE_PATH)

STATES = {
    'REGISTRATION_NAME': 'registration_name',
    'REGISTRATION_AGE': 'registration_age',
    'REGISTRATION_GENDER': 'registration_gender',
    'REGISTRATION_LOOKING_FOR': 'registration_looking_for',
    'REGISTRATION_BIO': 'registration_bio',
    'REGISTRATION_PHOTO': 'registration_photo',
    'REGISTRATION_CITY': 'registration_city',
    'CHATTING': 'chatting',
}

GIFT_CATALOG = {
    'rose': {'name': '🌹 Rose', 'stars': 1},
    'heart': {'name': '💖 Heart', 'stars': 3},
    'cake': {'name': '🎂 Cake', 'stars': 5},
}


def get_share_link(user_id: int) -> str:
    username = (BOT_USERNAME or '').strip().replace('@', '')
    if not username:
        return 'https://t.me/share/url?url=https://t.me&text=Join%20our%20dating%20bot'

    bot_link = f"https://t.me/{username}?start=ref_{user_id}"
    return f"https://t.me/share/url?url={bot_link}&text=Join%20me%20in%20this%20dating%20bot"


def get_open_mini_app_markup() -> InlineKeyboardMarkup | None:
    if not MINI_APP_URL:
        return None
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]
    ])


async def notify_user_liked(context: ContextTypes.DEFAULT_TYPE, from_user_id: int, to_user_id: int):
    if from_user_id == to_user_id:
        return
    sender = db.get_user(from_user_id)
    sender_name = (sender or {}).get("name") or "Someone"
    try:
        await context.bot.send_message(
            chat_id=to_user_id,
            text=f"❤️ {sender_name} liked you!\n\nOpen Mini App to check likes and matches.",
            reply_markup=get_open_mini_app_markup(),
        )
    except Exception as e:
        logger.error(f"Failed to send like notification: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if MINI_APP_URL:
        await update.message.reply_text(
            "Открой Mini App — свайпы, чат и профиль работают внутри приложения.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]
            ])
        )
        return

    if db.user_exists(user.id):
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            f"{WELCOME_MESSAGE}\n\n"
            "Let's create your profile! 💫\n\n"
            "What's your name?"
        )
        db.set_user_state(user.id, STATES['REGISTRATION_NAME'])

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Start Swiping", callback_data="swipe")],
        [InlineKeyboardButton("💬 My Matches", callback_data="matches")],
        [InlineKeyboardButton("🎁 Gifts", callback_data="gifts")],
        [InlineKeyboardButton("👀 Who Liked Me", callback_data="who_liked_me")],
        [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton("🤝 Share Bot", callback_data="share")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ]

    if MINI_APP_URL:
        keyboard.insert(0, [InlineKeyboardButton("📱 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_data = db.get_user(update.effective_user.id)
    matches_count = len(db.get_matches(update.effective_user.id))
    likes_count = len(db.get_who_liked_me(update.effective_user.id))
    
    text = (
        f"Welcome back, {user_data['name']}! 💕\n\n"
        f"💬 Matches: {matches_count}\n"
        f"❤️ Likes: {likes_count}\n\n"
        f"What would you like to do?"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state, data = db.get_user_state(user_id)
    
    if state == STATES['REGISTRATION_NAME']:
        name = update.message.text.strip()
        db.set_user_state(user_id, STATES['REGISTRATION_AGE'], {'name': name})
        await update.message.reply_text("Great! How old are you? (Enter your age as a number)")
    
    elif state == STATES['REGISTRATION_AGE']:
        try:
            age = int(update.message.text.strip())
            if age < 18 or age > 100:
                await update.message.reply_text("Please enter a valid age (18-100)")
                return
            
            data['age'] = age
            keyboard = [
                [InlineKeyboardButton("👨 Male", callback_data="gender_male")],
                [InlineKeyboardButton("👩 Female", callback_data="gender_female")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            db.set_user_state(user_id, STATES['REGISTRATION_GENDER'], data)
            await update.message.reply_text("What's your gender?", reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("Please enter a valid number for your age")
    
    elif state == STATES['REGISTRATION_BIO']:
        bio = update.message.text.strip()
        data['bio'] = bio
        db.set_user_state(user_id, STATES['REGISTRATION_PHOTO'], data)
        await update.message.reply_text(
            "Great! Now send me your best photo 📸\n\n"
            "Or type /skip to use a default avatar"
        )
    
    elif state == STATES['REGISTRATION_PHOTO']:
        if update.message.photo:
            try:
                photo = update.message.photo[-1]
                
                # Проверка размера файла
                try:
                    file = await context.bot.get_file(photo.file_id)
                    file_size_mb = file.file_size / (1024 * 1024)
                    
                    if file_size_mb > 10:
                        await update.message.reply_text(
                            f"❌ Фото слишком большое! Максимум 10 МБ.\n"
                            f"Текущий размер: {file_size_mb:.1f} МБ\n\n"
                            f"Пожалуйста, отправьте фото меньшего размера или /skip"
                        )
                        return
                except Exception as e:
                    logger.error(f"Error checking file size: {e}")
                    # Продолжаем даже если не удалось проверить размер
                
                photo_id = photo.file_id
                data['photo_id'] = photo_id
                db.set_user_state(user_id, STATES['REGISTRATION_CITY'], data)
                
                cities = get_city_keyboard()
                keyboard = []
                for i in range(0, len(cities), 2):
                    row = []
                    row.append(InlineKeyboardButton(cities[i]['display'], callback_data=f"city_{cities[i]['id']}"))
                    if i + 1 < len(cities):
                        row.append(InlineKeyboardButton(cities[i+1]['display'], callback_data=f"city_{cities[i+1]['id']}"))
                    keyboard.append(row)
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Perfect! В каком городе вы находитесь?\n\nВыберите город из списка:",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error processing photo: {e}")
                await update.message.reply_text(
                    "❌ Ошибка при обработке фото. Попробуйте ещё раз или /skip"
                )
        else:
            await update.message.reply_text("Please send a photo or type /skip")
    
    elif state == STATES['REGISTRATION_CITY']:
        await update.message.reply_text("Пожалуйста, выберите город из списка кнопок выше.")
    
    elif state == 'EDIT_NAME':
        new_name = update.message.text.strip()
        conn = db.get_connection()
        conn.execute('UPDATE users SET name = ? WHERE user_id = ?', (new_name, user_id))
        conn.commit()
        conn.close()
        db.clear_user_state(user_id)
        await update.message.reply_text(f"✅ Имя изменено на: {new_name}")
        await show_main_menu(update, context)
    
    elif state == 'EDIT_AGE':
        try:
            new_age = int(update.message.text.strip())
            if 18 <= new_age <= 100:
                conn = db.get_connection()
                conn.execute('UPDATE users SET age = ? WHERE user_id = ?', (new_age, user_id))
                conn.commit()
                conn.close()
                db.clear_user_state(user_id)
                await update.message.reply_text(f"✅ Возраст изменён на: {new_age}")
                await show_main_menu(update, context)
            else:
                await update.message.reply_text("Введите возраст от 18 до 100")
        except ValueError:
            await update.message.reply_text("Введите корректный возраст (число)")
    
    elif state == 'EDIT_BIO':
        new_bio = update.message.text.strip()
        conn = db.get_connection()
        conn.execute('UPDATE users SET bio = ? WHERE user_id = ?', (new_bio, user_id))
        conn.commit()
        conn.close()
        db.clear_user_state(user_id)
        await update.message.reply_text("✅ Описание обновлено!")
        await show_main_menu(update, context)
    
    elif state == 'EDIT_PHOTO':
        if update.message.photo:
            try:
                photo = update.message.photo[-1]
                
                # Проверка размера файла
                try:
                    file = await context.bot.get_file(photo.file_id)
                    file_size_mb = file.file_size / (1024 * 1024)
                    
                    if file_size_mb > 10:
                        await update.message.reply_text(
                            f"❌ Фото слишком большое! Максимум 10 МБ.\n"
                            f"Текущий размер: {file_size_mb:.1f} МБ"
                        )
                        return
                except Exception as e:
                    logger.error(f"Error checking file size: {e}")
                    # Продолжаем даже если не удалось проверить размер
                
                new_photo_id = photo.file_id
                conn = db.get_connection()
                conn.execute('UPDATE users SET photo_id = ? WHERE user_id = ?', (new_photo_id, user_id))
                conn.commit()
                conn.close()
                db.clear_user_state(user_id)
                await update.message.reply_text("✅ Фото обновлено!")
                await show_main_menu(update, context)
            except Exception as e:
                logger.error(f"Error updating photo: {e}")
                await update.message.reply_text(
                    "❌ Ошибка при обновлении фото. Попробуйте ещё раз."
                )
        else:
            await update.message.reply_text("Пожалуйста, отправьте фото")
    
    elif state == STATES['CHATTING']:
        if data and 'chat_with' in data:
            chat_with_id = data['chat_with']
            
            if not db.is_match(user_id, chat_with_id):
                await update.message.reply_text("You can only chat with your matches!")
                db.clear_user_state(user_id)
                return
            
            message_text = (update.message.text or '').strip()
            if not message_text:
                await update.message.reply_text("Введите текст сообщения")
                return

            if len(message_text) > 2000:
                await update.message.reply_text("Сообщение слишком длинное (макс. 2000 символов)")
                return

            db.save_message(user_id, chat_with_id, message_text)
            db.update_message_stats(user_id, chat_with_id)
            await update.message.reply_text("✅ Сообщение отправлено!")
            
            try:
                chat_with_user = db.get_user(chat_with_id)
                await context.bot.send_message(
                    chat_id=chat_with_id,
                    text=f"💬 Новое сообщение от {db.get_user(user_id)['name']}:\n\n{message_text}\n\n"
                         f"Ответьте через My Matches → {db.get_user(user_id)['name']}"
                )
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data_parts = query.data.split('_')
    action = data_parts[0]
    
    if action == "swipe":
        await show_next_candidate(update, context)
    
    elif action == "like":
        candidate_id = int(data_parts[1])
        db.update_like_stats(user_id, candidate_id)
        is_match = db.add_like(user_id, candidate_id)
        await notify_user_liked(context, user_id, candidate_id)
        
        if is_match:
            db.update_match_stats(user_id, candidate_id)
        
        if is_match:
            candidate = db.get_user(candidate_id)
            await query.edit_message_text(
                f"🎉 It's a Match! 🎉\n\n"
                f"You and {candidate['name']} liked each other!\n\n"
                f"Start chatting now! 💬"
            )
            
            try:
                user = db.get_user(user_id)
                await context.bot.send_message(
                    chat_id=candidate_id,
                    text=f"🎉 New Match! 🎉\n\n{user['name']} likes you too!"
                )
            except Exception as e:
                logger.error(f"Failed to notify match: {e}")
            
            await context.bot.send_message(
                chat_id=user_id,
                text="Continue swiping?",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔥 Keep Swiping", callback_data="swipe"),
                    InlineKeyboardButton("🏠 Main Menu", callback_data="menu")
                ]])
            )
        else:
            await query.edit_message_text("❤️ Like sent!")
            await show_next_candidate(update, context)
    
    elif action == "dislike":
        await query.edit_message_text("👎 Passed")
        await show_next_candidate(update, context)
    
    elif action == "matches":
        await show_matches(update, context)

    elif action == "gifts":
        await show_gift_matches(update, context)

    elif action == "giftto":
        gift_to_user_id = int(data_parts[1])
        await show_gift_options(update, context, gift_to_user_id)

    elif action == "sendgift":
        gift_to_user_id = int(data_parts[1])
        gift_code = data_parts[2]
        await start_gift_payment(update, context, gift_to_user_id, gift_code)

    elif action == "paygift":
        gift_to_user_id = int(data_parts[1])
        gift_code = data_parts[2]
        await start_gift_payment(update, context, gift_to_user_id, gift_code)

    elif action == "receivedgifts":
        await show_received_gifts(update, context)

    elif action == "share":
        await show_share_menu(update, context)
    
    elif action == "chat":
        chat_with_id = int(data_parts[1])
        await start_chat(update, context, chat_with_id)
    
    elif action == "viewchat":
        chat_with_id = int(data_parts[1])
        await view_chat_history(update, context, chat_with_id)
    
    elif action == "menu":
        await show_main_menu(update, context)
    
    elif action == "profile":
        await show_profile(update, context)
    
    elif action == "gender":
        state, reg_data = db.get_user_state(user_id)
        gender = data_parts[1]
        reg_data['gender'] = gender
        
        keyboard = [
            [InlineKeyboardButton("👨 Male", callback_data="looking_male")],
            [InlineKeyboardButton("👩 Female", callback_data="looking_female")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        db.set_user_state(user_id, STATES['REGISTRATION_LOOKING_FOR'], reg_data)
        await query.edit_message_text("Who are you looking for?", reply_markup=reply_markup)
    
    elif action == "looking":
        state, reg_data = db.get_user_state(user_id)
        looking_for = data_parts[1]
        reg_data['looking_for'] = looking_for
        db.set_user_state(user_id, STATES['REGISTRATION_BIO'], reg_data)
        await query.edit_message_text("Tell us a bit about yourself! Write a short bio:")
    
    elif action == "who":
        await show_who_liked_me(update, context)
    
    elif action == "city":
        state, reg_data = db.get_user_state(user_id)
        if state == STATES['REGISTRATION_CITY']:
            city_id = data_parts[1]
            city_name = get_city_name(city_id)
            reg_data['city'] = city_name
            reg_data['city_id'] = city_id
            await complete_registration(update, context, reg_data)
        else:
            city_id = data_parts[1]
            city_name = get_city_name(city_id)
            db.get_connection().execute(
                'UPDATE users SET city = ? WHERE user_id = ?',
                (city_name, user_id)
            )
            db.get_connection().commit()
            db.clear_user_state(user_id)
            await query.answer(f"Город изменён на {get_city_display(city_id)}")
            await show_profile(update, context)
    
    elif action == "edit":
        field = data_parts[1] if len(data_parts) > 1 else None
        if field == "profile":
            await start_profile_edit(update, context)
        elif field == "name":
            db.set_user_state(user_id, 'EDIT_NAME', {})
            await query.edit_message_text("Введите новое имя:")
        elif field == "age":
            db.set_user_state(user_id, 'EDIT_AGE', {})
            await query.edit_message_text("Введите новый возраст:")
        elif field == "bio":
            db.set_user_state(user_id, 'EDIT_BIO', {})
            await query.edit_message_text("Введите новое описание:")
        elif field == "photo":
            db.set_user_state(user_id, 'EDIT_PHOTO', {})
            await query.edit_message_text("Отправьте новое фото:")
        elif field == "city":
            cities = get_city_keyboard()
            keyboard = []
            for i in range(0, len(cities), 2):
                row = []
                row.append(InlineKeyboardButton(cities[i]['display'], callback_data=f"city_{cities[i]['id']}"))
                if i + 1 < len(cities):
                    row.append(InlineKeyboardButton(cities[i+1]['display'], callback_data=f"city_{cities[i+1]['id']}"))
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="edit_profile")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Выберите новый город:", reply_markup=reply_markup)
        else:
            await start_profile_edit(update, context)
    
    elif action == "writemsg":
        chat_with_id = int(data_parts[1])
        await query.answer("Теперь просто напишите сообщение в чат! ✍️")
        db.set_user_state(user_id, STATES['CHATTING'], {'chat_with': chat_with_id})
    
    elif action == "settings":
        await show_settings(update, context)
    
    elif action == "agefilter":
        await show_age_filter(update, context)
    
    elif action == "setage":
        min_age = int(data_parts[1])
        max_age = int(data_parts[2])
        db.set_age_filter(user_id, min_age, max_age)
        await query.answer(f"✅ Фильтр установлен: {min_age}-{max_age} лет")
        await show_settings(update, context)

async def show_next_candidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    candidates = db.get_candidates(user_id, limit=1)
    
    if candidates:
        db.track_profile_view(user_id, candidates[0]['user_id'])
    
    if not candidates:
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "No more profiles right now! 😔\n\nCheck back later for new people!",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "No more profiles right now! 😔\n\nCheck back later for new people!",
                reply_markup=reply_markup
            )
        return
    
    candidate = candidates[0]
    
    keyboard = [
        [
            InlineKeyboardButton("❌ Pass", callback_data=f"dislike_{candidate['user_id']}"),
            InlineKeyboardButton("❤️ Like", callback_data=f"like_{candidate['user_id']}")
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    profile_text = (
        f"{candidate['name']}, {candidate['age']}\n"
        f"📍 {candidate.get('city', 'Unknown')}\n\n"
        f"{candidate.get('bio', 'No bio yet')}"
    )
    
    if candidate.get('photo_id'):
        if update.callback_query:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=candidate['photo_id'],
                caption=profile_text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_photo(
                photo=candidate['photo_id'],
                caption=profile_text,
                reply_markup=reply_markup
            )
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text(profile_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(profile_text, reply_markup=reply_markup)

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    matches = db.get_matches(user_id)
    
    if not matches:
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "You don't have any matches yet! 😔\n\nKeep swiping to find your match!",
            reply_markup=reply_markup
        )
        return
    
    keyboard = []
    for match in matches[:10]:
        unread = db.get_unread_count(user_id)
        badge = f" ({unread} new)" if unread > 0 else ""
        keyboard.append([
            InlineKeyboardButton(
                f"💬 {match['name']}, {match['age']}{badge}",
                callback_data=f"chat_{match['user_id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"💕 Your Matches ({len(matches)}):\n\nSelect someone to chat with:",
        reply_markup=reply_markup
    )

async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_with_id: int):
    user_id = update.effective_user.id
    
    if not db.is_match(user_id, chat_with_id):
        await update.callback_query.answer("You can only chat with matches!", show_alert=True)
        return
    
    db.set_user_state(user_id, STATES['CHATTING'], {'chat_with': chat_with_id})
    db.mark_messages_read(user_id, chat_with_id)
    
    chat_with = db.get_user(chat_with_id)
    
    keyboard = [
        [InlineKeyboardButton("✍️ Написать сообщение", callback_data=f"writemsg_{chat_with_id}")],
        [InlineKeyboardButton("🎁 Отправить подарок", callback_data=f"giftto_{chat_with_id}")],
        [InlineKeyboardButton("📜 View Chat History", callback_data=f"viewchat_{chat_with_id}")],
        [InlineKeyboardButton("🔙 Back to Matches", callback_data="matches")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"💬 Общение с {chat_with['name']}\n\n"
        f"Нажмите '✍️ Написать сообщение' и отправьте текст в чат.\n"
        f"Все сообщения будут доставлены {chat_with['name']}.\n\n"
        f"Для выхода из режима чата используйте кнопки ниже.",
        reply_markup=reply_markup
    )

async def view_chat_history(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_with_id: int):
    user_id = update.effective_user.id
    messages = db.get_messages(user_id, chat_with_id, limit=20)
    
    if not messages:
        await update.callback_query.answer("No messages yet! Start the conversation!", show_alert=True)
        return
    
    chat_with = db.get_user(chat_with_id)
    user = db.get_user(user_id)
    
    chat_text = f"💬 Chat with {chat_with['name']}\n\n"
    
    for msg in messages:
        sender_name = user['name'] if msg['from_user_id'] == user_id else chat_with['name']
        chat_text += f"{sender_name}: {msg['message']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Chat", callback_data=f"chat_{chat_with_id}")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(chat_text, reply_markup=reply_markup)


async def show_gift_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    matches = db.get_matches(user_id)

    keyboard = []
    for match in matches[:10]:
        keyboard.append([InlineKeyboardButton(f"🎁 {match['name']}", callback_data=f"giftto_{match['user_id']}")])

    keyboard.append([InlineKeyboardButton("📥 Received Gifts", callback_data="receivedgifts")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="menu")])

    text = "Выберите match, чтобы отправить подарок:"
    if not matches:
        text = "У вас пока нет matches для отправки подарков."

    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_gift_options(update: Update, context: ContextTypes.DEFAULT_TYPE, gift_to_user_id: int):
    user_id = update.effective_user.id
    if not db.is_match(user_id, gift_to_user_id):
        await update.callback_query.answer("Подарки можно отправлять только match-пользователям", show_alert=True)
        return

    gift_to_user = db.get_user(gift_to_user_id)
    keyboard = []
    for gift_code, gift_data in GIFT_CATALOG.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{gift_data['name']} · {gift_data['stars']}⭐",
                callback_data=f"paygift_{gift_to_user_id}_{gift_code}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="gifts")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="menu")])

    await update.callback_query.edit_message_text(
        f"Выберите подарок для {gift_to_user['name']}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, gift_to_user_id: int, gift_code: str):
    user_id = update.effective_user.id
    if not db.is_match(user_id, gift_to_user_id):
        await update.callback_query.answer("Подарки можно отправлять только match-пользователям", show_alert=True)
        return

    gift = GIFT_CATALOG.get(gift_code)
    if not gift:
        await update.callback_query.answer("Подарок не найден", show_alert=True)
        return

    db.send_gift(user_id, gift_to_user_id, gift_code, gift['name'])

    try:
        sender = db.get_user(user_id)
        await context.bot.send_message(
            chat_id=gift_to_user_id,
            text=f"🎁 Вам подарок от {sender['name']}: {gift['name']}"
        )
    except Exception as e:
        logger.error(f"Failed to send gift notification: {e}")

    await update.callback_query.edit_message_text(
        f"Подарок {gift['name']} отправлен!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Send another", callback_data=f"giftto_{gift_to_user_id}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ])
    )


async def show_received_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    gifts = db.get_received_gifts(user_id, limit=20)
    if not gifts:
        text = "У вас пока нет полученных подарков."
    else:
        lines = ["📥 Ваши подарки:"]
        for gift in gifts:
            lines.append(f"• {gift['gift_name']} от {gift['from_name']}")
        text = "\n".join(lines)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Send Gift", callback_data="gifts")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ])
    )


async def show_share_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    share_url = get_share_link(user_id)
    await update.callback_query.edit_message_text(
        "Поделитесь ботом с друзьями:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Поделиться", url=share_url)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ])
    )

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    recent_gifts = db.get_received_gifts(user_id, limit=3)
    if recent_gifts:
        gifts_block = "\n".join([f"• {g['gift_name']} от {g['from_name']}" for g in recent_gifts])
    else:
        gifts_block = "Пока нет подарков"

    profile_text = (
        f"👤 Your Profile\n\n"
        f"Name: {user['name']}\n"
        f"Age: {user['age']}\n"
        f"Gender: {user['gender']}\n"
        f"Looking for: {user['looking_for']}\n"
        f"City: {user.get('city', 'Not set')}\n\n"
        f"Bio: {user.get('bio', 'No bio')}\n\n"
        f"🎁 Gifts:\n{gifts_block}"
    )
    
    keyboard = [
        [InlineKeyboardButton("✏️ Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if user.get('photo_id'):
        await context.bot.send_photo(
            chat_id=user_id,
            photo=user['photo_id'],
            caption=profile_text,
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(profile_text, reply_markup=reply_markup)

async def show_who_liked_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if db.has_paid_for_feature(user_id, 'see_likes'):
        likes = db.get_who_liked_me(user_id)
        
        if not likes:
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                "No one has liked you yet! 😔\n\nKeep your profile active!",
                reply_markup=reply_markup
            )
            return
        
        text = f"❤️ People who liked you ({len(likes)}):\n\n"
        for like in likes[:10]:
            text += f"• {like['name']}, {like['age']} - {like.get('city', 'Unknown')}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔥 Start Swiping", callback_data="swipe")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        likes_count = len(db.get_who_liked_me(user_id))
        
        keyboard = [
            [InlineKeyboardButton(f"⭐ Unlock for {STARS_TO_SEE_LIKES} Stars", callback_data="pay_see_likes")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"👀 {likes_count} people liked you!\n\n"
            f"Unlock this feature to see who they are! ⭐\n\n"
            f"Cost: {STARS_TO_SEE_LIKES} Telegram Stars",
            reply_markup=reply_markup
        )

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "pay_see_likes":
        payload = f"feature:see_likes:{update.effective_user.id}"
        await send_invoice(
            update,
            context,
            title="See Who Liked You",
            description="Unlock the ability to see who liked your profile",
            payload=payload,
            label="See Likes",
            stars=STARS_TO_SEE_LIKES,
        )

async def send_invoice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    title: str,
    description: str,
    payload: str,
    label: str,
    stars: int,
):
    user_id = update.effective_user.id
    currency = "XTR"
    prices = [LabeledPrice(label, stars)]
    
    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payment = update.message.successful_payment

    payload = payment.invoice_payload or ""

    if payload.startswith("feature:"):
        payload_parts = payload.split(":")
        if len(payload_parts) < 3:
            await update.message.reply_text("✅ Payment received.")
            return

        feature = payload_parts[1]
        db.add_payment(user_id, payment.total_amount, feature, payment.telegram_payment_charge_id)

        await update.message.reply_text(
            "✅ Payment successful! Feature unlocked!\n\n"
            "You can now see who liked you! ❤️"
        )
        await show_who_liked_me(update, context)
        return

    if payload.startswith("gift:"):
        payload_parts = payload.split(":")
        if len(payload_parts) < 4:
            await update.message.reply_text("✅ Payment received.")
            return

        from_user_id = int(payload_parts[1])
        to_user_id = int(payload_parts[2])
        gift_code = payload_parts[3]

        if from_user_id != user_id:
            await update.message.reply_text("Платёж отклонён: пользователь не совпадает.")
            return

        if not db.is_match(from_user_id, to_user_id):
            await update.message.reply_text("Платёж получен, но пользователь больше не в matches.")
            return

        gift = GIFT_CATALOG.get(gift_code)
        if not gift:
            await update.message.reply_text("Платёж получен, но подарок не найден.")
            return

        db.send_gift(from_user_id, to_user_id, gift_code, gift['name'])
        db.add_payment(user_id, payment.total_amount, f"gift_{gift_code}_{to_user_id}", payment.telegram_payment_charge_id)

        try:
            sender = db.get_user(from_user_id)
            await context.bot.send_message(
                chat_id=to_user_id,
                text=f"🎁 Вам подарок от {sender['name']}: {gift['name']}"
            )
        except Exception as e:
            logger.error(f"Failed to send paid gift notification: {e}")

        await update.message.reply_text(f"✅ Подарок {gift['name']} отправлен!")
        return

    await update.message.reply_text("✅ Payment received.")

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    min_age = user.get('min_age', 18)
    max_age = user.get('max_age', 100)
    
    keyboard = [
        [InlineKeyboardButton(f"🎂 Возраст: {min_age}-{max_age} лет", callback_data="agefilter")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚙️ **Настройки**\n\n"
        f"Текущий фильтр возраста: **{min_age}-{max_age} лет**\n\n"
        "Нажмите на кнопку чтобы изменить фильтр."
    )
    
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_age_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("18-25", callback_data="setage_18_25"),
         InlineKeyboardButton("25-35", callback_data="setage_25_35")],
        [InlineKeyboardButton("35-45", callback_data="setage_35_45"),
         InlineKeyboardButton("45-60", callback_data="setage_45_60")],
        [InlineKeyboardButton("18-100 (Все)", callback_data="setage_18_100")],
        [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎂 Выберите диапазон возраста для поиска:",
        reply_markup=reply_markup
    )

async def start_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, field: str = None):
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("📝 Изменить имя", callback_data="edit_name")],
        [InlineKeyboardButton("🎂 Изменить возраст", callback_data="edit_age")],
        [InlineKeyboardButton("📍 Изменить город", callback_data="edit_city")],
        [InlineKeyboardButton("✍️ Изменить био", callback_data="edit_bio")],
        [InlineKeyboardButton("📸 Изменить фото", callback_data="edit_photo")],
        [InlineKeyboardButton("🔙 Назад к профилю", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "✏️ Редактирование профиля\n\nВыберите, что хотите изменить:",
        reply_markup=reply_markup
    )

async def skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state, data = db.get_user_state(user_id)
    
    if state == STATES['REGISTRATION_PHOTO']:
        data['photo_id'] = None
        db.set_user_state(user_id, STATES['REGISTRATION_CITY'], data)
        await update.message.reply_text("What city are you in? (Or type /skip)")
    
    elif state == STATES['REGISTRATION_CITY']:
        data['city'] = None
        await complete_registration(update, context, data)

async def complete_registration(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    user = update.effective_user
    
    db.create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        looking_for=data['looking_for'],
        bio=data.get('bio', ''),
        photo_id=data.get('photo_id'),
        city=data.get('city')
    )
    
    db.clear_user_state(user.id)
    
    await update.message.reply_text(
        "🎉 Registration complete!\n\n"
        "Welcome to the dating bot! Let's find your match! 💕"
    )
    
    await show_main_menu(update, context)

def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("skip", skip_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="^pay_"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    return application


def run_bot_polling(in_background_thread: bool = False):
    application = build_application()
    thread_loop = None

    run_polling_kwargs = {
        'allowed_updates': Update.ALL_TYPES,
    }
    if in_background_thread:
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)
        run_polling_kwargs['stop_signals'] = None

    try:
        application.run_polling(**run_polling_kwargs)
    finally:
        if thread_loop is not None and not thread_loop.is_closed():
            thread_loop.close()


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "="*50)
        print("⚠️  ERROR: Bot token not configured!")
        print("="*50)
        print("\n📝 Please follow these steps:\n")
        print("1. Open config.py")
        print("2. Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token")
        print("3. Get your token from @BotFather on Telegram")
        print("\n" + "="*50 + "\n")
        return
    
    print("\n" + "="*50)
    print("🤖 Bot is running!")
    print("="*50)
    print("\n✅ Bot started successfully!")
    print("💬 Open Telegram and start chatting with your bot\n")
    print("="*50 + "\n")

    run_bot_polling()

if __name__ == '__main__':
    main()
