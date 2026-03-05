# 💕 Tinder-like Telegram Dating Bot

A fully functional Tinder-style dating bot for Telegram with swipe functionality, matching system, in-app chat, and Telegram Stars payment integration.

## ✨ Features

- 🔥 **Swipe Interface** - Like or dislike profiles with simple buttons
- 💕 **Smart Matching** - Only matched users can chat with each other
- 💬 **In-App Chat** - All conversations happen inside the bot
- ⭐ **Premium Features** - See who liked you (paid with Telegram Stars)
- 📸 **Photo Profiles** - Users can upload profile photos
- 🎯 **Gender Preferences** - Filter by who you're looking for
- 📍 **Location** - Show your city
- 🔔 **Real-time Notifications** - Get notified about matches and messages

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/macbookprom1/CascadeProjects/tinder-tg-bot
pip install -r requirements.txt
```

### 2. Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 3. Configure Your Bot

Open `config.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 4. Run the Bot

```bash
python bot.py
```

That's it! Your bot is now running! 🎉

## 🎨 Customization Guide

### Change Bot Name and Welcome Message

Edit in `config.py`:
```python
BOT_NAME = "💕 Your Bot Name"
WELCOME_MESSAGE = "Your custom welcome message"
```

### Change Logo

1. Create an `assets` folder in the project directory
2. Add your logo image as `logo.png`
3. Update the path in `config.py`:
```python
LOGO_PATH = "assets/logo.png"
```

### Adjust Payment Price

Change the Stars amount in `config.py`:
```python
STARS_TO_SEE_LIKES = 10  # Change to your desired amount
```

### Add Admin Notifications

Add your Telegram user ID in `config.py`:
```python
ADMIN_USER_IDS = [123456789]  # Your Telegram user ID
```

## 📱 How It Works

### For Users:

1. **Start** - `/start` command begins registration
2. **Create Profile** - Enter name, age, gender, preferences, bio, photo, city
3. **Swipe** - Browse profiles and like/dislike
4. **Match** - When both users like each other, it's a match!
5. **Chat** - Matched users can chat directly in the bot
6. **Premium** - Pay with Telegram Stars to see who liked you

### Bot Commands:

- `/start` - Start the bot or return to main menu
- `/skip` - Skip optional registration steps

## 🗄️ Database Structure

The bot uses SQLite with the following tables:
- **users** - User profiles and information
- **likes** - Track who liked whom
- **matches** - Store mutual likes
- **messages** - In-app chat messages
- **payments** - Telegram Stars payment records
- **user_state** - Track registration progress

## 💳 Telegram Stars Payment

The bot integrates Telegram Stars for premium features:
- Users can pay to see who liked their profile
- Payment is processed securely through Telegram
- No external payment gateway needed
- All transactions are tracked in the database

## 🌐 Deployment Options

### Option 1: Local Machine (Testing)
```bash
python bot.py
```
Keep the terminal open. Bot stops when you close it.

### Option 2: VPS/Cloud Server (Production)

**Free Options:**
- **Railway.app** - Free tier available
- **Render.com** - Free tier available
- **Fly.io** - Free tier available
- **PythonAnywhere** - Free tier available

**Deployment Steps:**

1. Push your code to GitHub
2. Connect your repository to the hosting service
3. Set environment variable: `BOT_TOKEN=your_token_here`
4. Deploy!

### Option 3: Run with Screen (VPS)

```bash
screen -S dating-bot
python bot.py
# Press Ctrl+A then D to detach
# Reconnect with: screen -r dating-bot
```

### Option 4: Run with systemd (Linux VPS)

Create `/etc/systemd/system/dating-bot.service`:

```ini
[Unit]
Description=Telegram Dating Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tinder-tg-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable dating-bot
sudo systemctl start dating-bot
sudo systemctl status dating-bot
```

## 🔧 Troubleshooting

### Bot doesn't respond
- Check if bot token is correct in `config.py`
- Make sure `python bot.py` is running
- Check internet connection

### Payment not working
- Telegram Stars payments require bot to be verified
- Test in production environment (not local testing)
- Ensure you're using the correct currency code "XTR"

### Database errors
- Delete `dating_bot.db` file and restart bot
- Check file permissions

## 📝 File Structure

```
tinder-tg-bot/
├── bot.py              # Main bot logic
├── database.py         # Database operations
├── config.py           # Configuration (ADD YOUR TOKEN HERE)
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── dating_bot.db      # SQLite database (created automatically)
└── assets/            # Images and media (create this folder)
    ├── logo.png
    └── default_avatar.png
```

## 🎯 Next Steps

1. **Test the bot** - Create multiple test accounts to test matching
2. **Customize** - Change colors, messages, and features
3. **Deploy** - Move to a cloud server for 24/7 operation
4. **Promote** - Share your bot with users
5. **Monitor** - Check logs and user activity

## 💡 Tips

- Test with 2-3 Telegram accounts to verify matching works
- Add more profile fields (height, interests, etc.) in database.py
- Implement photo verification for safety
- Add reporting/blocking features
- Create admin panel for moderation
- Add analytics to track user engagement

## 🆘 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your bot token is correct
3. Ensure all dependencies are installed
4. Check Telegram Bot API status

## 📄 License

Free to use and modify for your projects!

---

**Made with ❤️ for connecting people**
