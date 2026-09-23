import os
from dotenv import load_dotenv

load_dotenv()  # .env faylidan o'zgaruvchilarni yuklaydi (lokal ishlashda qulay)

# Telegram bot tokeni (@BotFather dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")

# ---------------- AI provayderlar ----------------
# Har biri ixtiyoriy — kaliti bo'lmagan provayder avtomatik o'tkazib yuboriladi.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-1.5-flash"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

# Sinov tartibi: birinchisi ishlamasa (xato/limit/balans tugasa),
# avtomatik ravishda keyingisiga o'tiladi. Xohlagan tartibda qo'yishingiz mumkin.
AI_PROVIDER_ORDER = ["openai", "gemini", "claude"]

# Hozircha barcha foydalanuvchilar uchun bepul (limitsiz).
# Keyinchalik shu yerga kunlik/oylik limit yoki balans tizimi qo'shiladi.
FREE_MODE = True

# Reja (bo'lim) sonlari — foydalanuvchi shulardan birini tanlaydi
REJA_OPTIONS = [3, 4, 5]

# Varoq (sahifa) oralig'i variantlari — har biriga taxminiy so'z/belgi hajmi bog'langan
# (bitta A4 varoq ~ 1800-2000 belgi, standart 14pt, 1.5 interval hisobida)
VAROQ_OPTIONS = {
    "10-15": {"min_pages": 10, "max_pages": 15, "chars_per_section": 2200},
    "15-20": {"min_pages": 15, "max_pages": 20, "chars_per_section": 2800},
    "20-25": {"min_pages": 20, "max_pages": 25, "chars_per_section": 3400},
}

OUTPUT_DIR = "generated_docs"