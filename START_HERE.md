# 🚀 QUICK START - Read This First!

## ⚡ 3 Steps to Launch Your Bot

### Step 1: Get Your Bot Token 🤖

1. Open **Telegram** on your phone or computer
2. Search for **@BotFather**
3. Send this command: `/newbot`
4. Follow the instructions:
   - Choose a name for your bot (e.g., "My Dating Bot")
   - Choose a username (must end in 'bot', e.g., "mydating_bot")
5. **Copy the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Add Your Token 🔑

1. Open the file: **`config.py`**
2. Find this line:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
3. Replace `YOUR_BOT_TOKEN_HERE` with your actual token:
   ```python
   BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```
4. **Save the file**

### Step 3: Run Your Bot 🎉

Open Terminal and run these commands:

```bash
cd /Users/macbookprom1/CascadeProjects/tinder-tg-bot
pip install -r requirements.txt
python bot.py
```

**That's it!** Your bot is now running! 🎊

---

## 📱 Test Your Bot

1. Open Telegram
2. Search for your bot username (the one you created with @BotFather)
3. Click **Start**
4. Follow the registration process
5. Create a second test account to test matching!

---

## 🎨 Customization Locations

### Change Bot Name & Messages
**File:** `config.py`
```python
BOT_NAME = "💕 Dating Bot"  # Change this
WELCOME_MESSAGE = "Welcome to the Dating Bot! Find your match! 💕"  # Change this
```

### Change Payment Price
**File:** `config.py`
```python
STARS_TO_SEE_LIKES = 10  # Change to any number
```

### Add Your Logo
1. Create folder: `assets`
2. Add your logo as: `assets/logo.png`
3. Update in `config.py`:
```python
LOGO_PATH = "assets/logo.png"
```

---

## 🌐 Deploy for 24/7 Operation

Your bot currently runs only when your computer is on. To make it run 24/7:

**Read:** `DEPLOY.md` for free hosting options

**Recommended:** Railway.app or Render.com (both have free tiers)

---

## ✨ Features Included

✅ **Tinder-style swiping** (Like/Dislike)
✅ **Matching system** (mutual likes)
✅ **In-app chat** (only between matches)
✅ **Photo profiles**
✅ **Gender preferences**
✅ **City/location**
✅ **Telegram Stars payment** (see who liked you)
✅ **Real-time notifications**
✅ **Message history**

---

## 🆘 Troubleshooting

### Bot doesn't start?
- Check if you replaced `YOUR_BOT_TOKEN_HERE` in `config.py`
- Make sure you installed dependencies: `pip install -r requirements.txt`

### Bot doesn't respond?
- Make sure `python bot.py` is running in Terminal
- Check if the token is correct
- Try creating a new bot with @BotFather

### Payment not working?
- Telegram Stars only work in production (after deployment)
- Test locally without payment first

---

## 📞 Next Steps

1. ✅ Test the bot locally
2. 📝 Customize messages and settings
3. 🚀 Deploy to free hosting (see DEPLOY.md)
4. 📱 Share with users
5. 📊 Monitor and improve

---

## 📚 Documentation

- **README.md** - Full documentation
- **DEPLOY.md** - Deployment guide
- **config.py** - All settings (START HERE!)

---

**Need help?** Check README.md for detailed instructions!

**Ready to deploy?** Check DEPLOY.md for free hosting options!

---

Made with ❤️ - Happy matching! 💕
