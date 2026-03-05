# 🚀 Deployment Guide - Free Hosting Options

This guide shows you how to deploy your Telegram dating bot for **FREE** 24/7 operation.

## 🎯 Best Free Options

### ✅ Option 1: Railway.app (RECOMMENDED)

**Pros:** Easy setup, free tier, automatic deployments
**Free Tier:** $5 credit/month (enough for small bots)

#### Steps:

1. **Create Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add Environment Variables**
   - Go to Variables tab
   - Add: `BOT_TOKEN` = your_bot_token

4. **Create Procfile**
   Create a file named `Procfile` (no extension):
   ```
   worker: python bot.py
   ```

5. **Deploy**
   - Railway will automatically deploy
   - Check logs to verify it's running

---

### ✅ Option 2: Render.com

**Pros:** Generous free tier, easy to use
**Free Tier:** 750 hours/month

#### Steps:

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +"
   - Select "Background Worker"
   - Connect your GitHub repo

3. **Configure**
   - Name: dating-bot
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`

4. **Add Environment Variable**
   - Add: `BOT_TOKEN` = your_bot_token

5. **Deploy**
   - Click "Create Background Worker"

---

### ✅ Option 3: Fly.io

**Pros:** Good free tier, fast deployment
**Free Tier:** 3 shared VMs

#### Steps:

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Create fly.toml**
   Create `fly.toml` in your project:
   ```toml
   app = "your-dating-bot"
   
   [build]
     builder = "paketobuildpacks/builder:base"
   
   [[services]]
     internal_port = 8080
     protocol = "tcp"
   
     [[services.ports]]
       port = 80
   ```

4. **Deploy**
   ```bash
   fly launch
   fly secrets set BOT_TOKEN=your_bot_token_here
   fly deploy
   ```

---

### ✅ Option 4: PythonAnywhere

**Pros:** Simple, Python-focused
**Free Tier:** Limited but sufficient for small bots

#### Steps:

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Sign up for free account

2. **Upload Files**
   - Go to Files tab
   - Upload all your bot files

3. **Install Dependencies**
   - Open Bash console
   ```bash
   pip install --user python-telegram-bot
   ```

4. **Edit config.py**
   - Add your bot token

5. **Create Always-On Task**
   - Go to Tasks tab
   - Add: `python3 /home/yourusername/bot.py`

---

### ✅ Option 5: Heroku (With Limitations)

**Note:** Heroku removed free tier, but you can use eco dynos ($5/month) or student credits

#### Steps:

1. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create Procfile**
   ```
   worker: python bot.py
   ```

4. **Deploy**
   ```bash
   heroku create your-dating-bot
   heroku config:set BOT_TOKEN=your_bot_token_here
   git push heroku main
   heroku ps:scale worker=1
   ```

---

## 📋 Required Files for Deployment

### 1. Procfile
```
worker: python bot.py
```

### 2. runtime.txt (optional, specifies Python version)
```
python-3.11.0
```

### 3. .gitignore (don't commit sensitive data)
```
*.db
config.py
.env
__pycache__/
```

### 4. requirements.txt (already created)
```
python-telegram-bot==20.7
```

---

## 🔐 Environment Variables Method

Instead of hardcoding token in `config.py`, use environment variables:

### Update config.py:
```python
import os

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
```

### Set on hosting platform:
- Railway: Variables tab
- Render: Environment tab
- Fly.io: `fly secrets set BOT_TOKEN=xxx`
- Heroku: `heroku config:set BOT_TOKEN=xxx`

---

## 🧪 Testing Before Deployment

1. **Test Locally First**
   ```bash
   python bot.py
   ```

2. **Test with Multiple Accounts**
   - Create 2-3 test Telegram accounts
   - Test registration, swiping, matching, chatting

3. **Test Payment**
   - Telegram Stars only work in production
   - Test after deployment

---

## 📊 Monitoring Your Bot

### Check if bot is running:

**Railway:**
- Go to Deployments tab
- Check logs

**Render:**
- Go to Logs tab
- View real-time logs

**Fly.io:**
```bash
fly logs
```

**PythonAnywhere:**
- Check error logs in Files tab

---

## 🔧 Common Deployment Issues

### Bot not responding
```bash
# Check logs for errors
# Verify BOT_TOKEN is set correctly
# Ensure worker/process is running
```

### Database issues
```bash
# SQLite works on all platforms
# Database file is created automatically
# Make sure write permissions exist
```

### Import errors
```bash
# Verify requirements.txt is correct
# Check Python version compatibility
# Reinstall dependencies
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| Railway | $5 credit/month | ~500 hours |
| Render | 750 hours/month | Sleeps after 15min inactive |
| Fly.io | 3 VMs free | 160GB bandwidth |
| PythonAnywhere | Always-on task | CPU/bandwidth limits |
| Heroku | No free tier | $5/month minimum |

---

## 🎯 Recommended Setup

**For Testing:**
- Run locally: `python bot.py`

**For Production (Small Scale):**
- Use Railway.app or Render.com
- Set up GitHub auto-deployment
- Monitor logs regularly

**For Production (Large Scale):**
- Use dedicated VPS (DigitalOcean, Linode)
- Set up monitoring (Sentry, etc.)
- Use PostgreSQL instead of SQLite
- Implement caching (Redis)

---

## 📱 After Deployment

1. **Test the bot** on Telegram
2. **Share the bot link** with users
3. **Monitor logs** for errors
4. **Check database** growth
5. **Optimize** based on usage

---

## 🆘 Need Help?

- Check platform documentation
- Review bot logs for errors
- Test locally first
- Verify all environment variables are set

---

**Your bot is ready to connect people! 💕**
