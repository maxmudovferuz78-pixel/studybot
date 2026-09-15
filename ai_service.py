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


async def generate_section(mavzu: str, bolim_nomi: str, chars_target: int, is_kirish: bool = False, is_xulosa: bool = False) -> str:
    """
    Bitta bo'lim (yoki Kirish/Xulosa) uchun matn generatsiya qiladi.
    chars_target — taxminiy belgi soni, sahifa hajmini nazorat qilish uchun.
    """
    if is_kirish:
        vazifa = f"'{mavzu}' mavzusidagi mustaqil ish uchun Kirish qismini yozing."
    elif is_xulosa:
        vazifa = f"'{mavzu}' mavzusidagi mustaqil ish uchun Xulosa qismini yozing."
    else:
        vazifa = f"'{mavzu}' mavzusi doirasida '{bolim_nomi}' bo'limi uchun batafsil matn yozing."

    prompt = (
        f"{vazifa}\n\n"
        f"Talablar:\n"
        f"- Rasmiy, akademik uslubda, o'zbek tilida yozing.\n"
        f"- Taxminan {chars_target} belgi (bir necha paragraf) hajmida bo'lsin.\n"
        f"- Sarlavha yozmang, faqat matnning o'zini bering.\n"
        f"- Paragraflarni mantiqiy tarzda ajrating.\n"
    )
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


