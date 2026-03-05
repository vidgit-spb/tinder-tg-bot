from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import ADMIN_USER_IDS, DATABASE_PATH

db = Database(DATABASE_PATH)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к админ-панели")
        return
    
    stats = db.get_admin_stats()
    top_users = db.get_top_users(limit=10)
    
    text = "📊 **АДМИН-ПАНЕЛЬ**\n\n"
    text += "**Общая статистика:**\n"
    text += f"👥 Всего пользователей: {stats['total_users']}\n"
    text += f"💕 Всего матчей: {stats['total_matches']}\n"
    text += f"💬 Всего сообщений: {stats['total_messages']}\n"
    text += f"💰 Всего платежей: {stats['total_payments']}\n"
    text += f"⭐ Всего Stars: {stats['total_stars']}\n\n"
    
    text += f"📈 Новые пользователи:\n"
    text += f"• За 24 часа: {stats['new_users_24h']}\n"
    text += f"• За 7 дней: {stats['new_users_7d']}\n\n"
    
    text += "🏆 **ТОП-10 пользователей** (по % лайков):\n\n"
    
    for i, user in enumerate(top_users, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{emoji} **{user['name']}**, {user['age']}\n"
        text += f"   📍 {user['city'] or 'Не указан'}\n"
        text += f"   👁️ Просмотров: {user['total_views']}\n"
        text += f"   ❤️ Лайков: {user['total_likes_received']}\n"
        text += f"   💕 Матчей: {user['total_matches']}\n"
        text += f"   📊 % лайков: **{user['like_rate']}%**\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")],
        [InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_detailed")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await query.answer("⛔ У вас нет доступа", show_alert=True)
        return
    
    if query.data == "admin_refresh":
        stats = db.get_admin_stats()
        top_users = db.get_top_users(limit=10)
        
        text = "📊 **АДМИН-ПАНЕЛЬ**\n\n"
        text += "**Общая статистика:**\n"
        text += f"👥 Всего пользователей: {stats['total_users']}\n"
        text += f"💕 Всего матчей: {stats['total_matches']}\n"
        text += f"💬 Всего сообщений: {stats['total_messages']}\n"
        text += f"💰 Всего платежей: {stats['total_payments']}\n"
        text += f"⭐ Всего Stars: {stats['total_stars']}\n\n"
        
        text += f"📈 Новые пользователи:\n"
        text += f"• За 24 часа: {stats['new_users_24h']}\n"
        text += f"• За 7 дней: {stats['new_users_7d']}\n\n"
        
        text += "🏆 **ТОП-10 пользователей** (по % лайков):\n\n"
        
        for i, user in enumerate(top_users, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{emoji} **{user['name']}**, {user['age']}\n"
            text += f"   📍 {user['city'] or 'Не указан'}\n"
            text += f"   👁️ Просмотров: {user['total_views']}\n"
            text += f"   ❤️ Лайков: {user['total_likes_received']}\n"
            text += f"   💕 Матчей: {user['total_matches']}\n"
            text += f"   📊 % лайков: **{user['like_rate']}%**\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")],
            [InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_detailed")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == "admin_detailed":
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT gender, COUNT(*) as count FROM users GROUP BY gender')
        gender_stats = cursor.fetchall()
        
        cursor.execute('SELECT city, COUNT(*) as count FROM users GROUP BY city ORDER BY count DESC LIMIT 5')
        city_stats = cursor.fetchall()
        
        cursor.execute('SELECT AVG(age) as avg_age FROM users')
        avg_age = cursor.fetchone()['avg_age']
        
        conn.close()
        
        text = "📊 **Детальная статистика**\n\n"
        text += "**По полу:**\n"
        for stat in gender_stats:
            text += f"• {stat['gender']}: {stat['count']}\n"
        
        text += f"\n**Средний возраст:** {avg_age:.1f} лет\n\n"
        
        text += "**Топ-5 городов:**\n"
        for i, stat in enumerate(city_stats, 1):
            text += f"{i}. {stat['city'] or 'Не указан'}: {stat['count']}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
