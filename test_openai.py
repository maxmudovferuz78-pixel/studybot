"""
OpenAI ulanishini alohida sinash uchun.
Ishga tushirish: python test_openai.py
"""
import asyncio
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


async def main():
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY .env faylida topilmadi yoki bo'sh!")
        return

    print(f"Kalit topildi: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")
    print(f"Model: {OPENAI_MODEL}")
    print("Sinov so'rovi yuborilmoqda...")

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
