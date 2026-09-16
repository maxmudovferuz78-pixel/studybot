import os
from dotenv import load_dotenv

load_dotenv()  # .env faylidan o'zgaruvchilarni yuklaydi (lokal ishlashda qulay)

# Telegram bot tokeni (@BotFather dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")

# OpenAI API kaliti (platform.openai.com dan olinadi)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SIZNING_OPENAI_KEYINGIZ")

# Ishlatiladigan model — arzon va sifatli variant
OPENAI_MODEL = "gpt-4o-mini"

# Hozircha barcha foydalanuvchilar uchun bepul (limitsiz).
# Keyinchalik shu yerga kunlik/oylik limit yoki balans tizimi qo'shiladi.
FREE_MODE = True


