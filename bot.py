import logging
import os
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
)
from database import Database
from config import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
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
        [InlineKeyboardButton("👀 Who Liked Me", callback_data="who_liked_me")],
        [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
    ]
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
                [InlineKeyboardButton("🌈 Other", callback_data="gender_other")],
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
            photo_id = update.message.photo[-1].file_id
            data['photo_id'] = photo_id
            db.set_user_state(user_id, STATES['REGISTRATION_CITY'], data)
            await update.message.reply_text("Perfect! What city are you in? (Or type /skip)")
        else:
            await update.message.reply_text("Please send a photo or type /skip")
    
    elif state == STATES['REGISTRATION_CITY']:
        city = update.message.text.strip()
        data['city'] = city
        await complete_registration(update, context, data)
    
    elif state == STATES['CHATTING']:
        if data and 'chat_with' in data:
            chat_with_id = data['chat_with']
            
            if not db.is_match(user_id, chat_with_id):
                await update.message.reply_text("You can only chat with your matches!")
                db.clear_user_state(user_id)
                return
            
            db.save_message(user_id, chat_with_id, update.message.text)
            await update.message.reply_text("✅ Message sent!")
            
            try:
                chat_with_user = db.get_user(chat_with_id)
                await context.bot.send_message(
                    chat_id=chat_with_id,
                    text=f"💬 New message from {db.get_user(user_id)['name']}:\n\n{update.message.text}\n\n"
                         f"Reply with /chat_{user_id} to continue the conversation"
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
        is_match = db.add_like(user_id, candidate_id)
        
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
            [InlineKeyboardButton("🌈 Everyone", callback_data="looking_everyone")],
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

async def show_next_candidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    candidates = db.get_candidates(user_id, limit=1)
    
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
        [InlineKeyboardButton("📜 View Chat History", callback_data=f"viewchat_{chat_with_id}")],
        [InlineKeyboardButton("🔙 Back to Matches", callback_data="matches")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"💬 Chatting with {chat_with['name']}\n\n"
        f"Send your message below! All messages will be delivered directly to {chat_with['name']}.\n\n"
        f"To exit chat mode, use the buttons below.",
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

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    profile_text = (
        f"👤 Your Profile\n\n"
        f"Name: {user['name']}\n"
        f"Age: {user['age']}\n"
        f"Gender: {user['gender']}\n"
        f"Looking for: {user['looking_for']}\n"
        f"City: {user.get('city', 'Not set')}\n\n"
        f"Bio: {user.get('bio', 'No bio')}"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]]
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
        await send_invoice(update, context, "see_likes", STARS_TO_SEE_LIKES)

async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, feature: str, stars: int):
    user_id = update.effective_user.id
    
    title = "See Who Liked You"
    description = f"Unlock the ability to see who liked your profile"
    payload = f"{feature}_{user_id}"
    currency = "XTR"
    prices = [LabeledPrice("See Likes", stars)]
    
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
    
    payload_parts = payment.invoice_payload.split('_')
    feature = payload_parts[0]
    
    db.add_payment(user_id, payment.total_amount, feature, payment.telegram_payment_charge_id)
    
    await update.message.reply_text(
        "✅ Payment successful! Feature unlocked!\n\n"
        "You can now see who liked you! ❤️"
    )
    
    await show_who_liked_me(update, context)

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
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("skip", skip_command))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="^pay_"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    print("\n" + "="*50)
    print("🤖 Bot is running!")
    print("="*50)
    print("\n✅ Bot started successfully!")
    print("💬 Open Telegram and start chatting with your bot\n")
    print("="*50 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
