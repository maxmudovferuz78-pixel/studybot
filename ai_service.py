"""
AI orqali mustaqil ish / referat matnini generatsiya qilish.
gpt-4o-mini ishlatiladi — arzon va o'zbek tilida sifatli akademik matn yozadi.
"""
import asyncio
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_reja(mavzu: str, reja_soni: int) -> list[str]:
    """
    Mavzu bo'yicha reja (bo'limlar ro'yxati) generatsiya qiladi.
    Masalan: ["Kirish", "1. ...", "2. ...", "Xulosa"]
    """
    prompt = (
        f"'{mavzu}' mavzusidagi mustaqil ish/referat uchun {reja_soni} ta "
        f"asosiy bo'limdan iborat reja tuzing. Kirish va Xulosa alohida "
        f"hisoblanmaydi, faqat asosiy {reja_soni} ta bo'lim nomini bering. "
        f"Har bir bo'lim nomini yangi qatordan, raqamlashtirib yozing. "
        f"Boshqa hech qanday izoh yozmang, faqat ro'yxat."
    )
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    text = response.choices[0].message.content.strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[:reja_soni]



