import os

# ========================================
# CONFIGURATION FILE
# ========================================
# This is where you configure your bot settings

# ========================================
# BOT TOKEN - REPLACE THIS WITH YOUR TOKEN
# ========================================
# Get your token from @BotFather on Telegram
# For production: set BOT_TOKEN environment variable
# For local: use .env file 
BOT_TOKEN = os.getenv('BOT_TOKEN', '8772849103:AAFgv4YIOlq9Fpv3iFdw0tL20nR73Iro95c')

# ========================================
# PAYMENT SETTINGS
# ========================================
# Cost in Telegram Stars to see who liked you
STARS_TO_SEE_LIKES = 1

# ========================================
# CUSTOMIZATION
# ========================================
# Bot name and description
BOT_NAME = "💕 Dating Bot"
WELCOME_MESSAGE = "Welcome to the Dating Bot! Find your match! 💕"

# ========================================
# PROFILE SETTINGS
# ========================================
# Maximum age difference for matching
MAX_AGE_DIFFERENCE = 10

# Maximum distance for matching (km) - set to None for unlimited
MAX_DISTANCE = None

# ========================================
# LOGO AND IMAGES
# ========================================
# Place your logo image in the 'assets' folder
# and update the filename here
LOGO_PATH = "assets/logo.png"

# Default profile photo if user doesn't upload one
DEFAULT_PROFILE_PHOTO = "assets/default_avatar.png"

# ========================================
# DATABASE
# ========================================
DATABASE_PATH = "dating_bot.db"

# ========================================
# ADMIN SETTINGS
# ========================================
# Add your Telegram user ID here to receive admin notifications
ADMIN_USER_IDS = [431713422, 431713422]
