"""
AI orqali mustaqil ish / referat matnini generatsiya qilish.

Uchta provayder qo'llab-quvvatlanadi: Gemini, OpenAI, Claude.
config.AI_PROVIDER_ORDER dagi tartib bo'yicha sinaladi — biri xato bersa
(kalit yo'q, balans tugagan, tarmoq xatosi va h.k.) avtomatik keyingisiga o'tiladi.
"""
import asyncio
import logging

from config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    AI_PROVIDER_ORDER,
)

logger = logging.getLogger(__name__)

# Har bir provayder klienti faqat kaliti mavjud bo'lsa yaratiladi
_openai_client = None
_anthropic_client = None
_gemini_client = None

if OPENAI_API_KEY:
    from openai import AsyncOpenAI
    _openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

if ANTHROPIC_API_KEY:
    from anthropic import AsyncAnthropic
    _anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

if GEMINI_API_KEY:
    # Yangi google-genai SDK (eski google-generativeai butunlay bekor qilingan)
    from google import genai
    _gemini_client = genai.Client(api_key=GEMINI_API_KEY)


async def _call_openai(prompt: str, max_tokens: int) -> str:
    if not _openai_client:
        raise RuntimeError("OpenAI kaliti sozlanmagan")
    response = await _openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


async def _call_gemini(prompt: str, max_tokens: int) -> str:
    if not _gemini_client:
        raise RuntimeError("Gemini kaliti sozlanmagan")
    # Yangi SDK sinxron — alohida threadda ishlatib event loopni bloklamaymiz
    response = await asyncio.to_thread(
        _gemini_client.models.generate_content,
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip()


async def _call_claude(prompt: str, max_tokens: int) -> str:
    if not _anthropic_client:
        raise RuntimeError("Claude kaliti sozlanmagan")
    response = await _anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


_PROVIDER_FUNCS = {
    "openai": _call_openai,
    "gemini": _call_gemini,
    "claude": _call_claude,
}


async def ask_ai(prompt: str, max_tokens: int = 2000) -> str:
    """
    AI_PROVIDER_ORDER tartibida provayderlarni sinab ko'radi.
    Biri xato bersa keyingisiga o'tadi. Hammasi xato bersa — istisno chiqaradi.
    """
    last_error = None
    for provider_name in AI_PROVIDER_ORDER:
        func = _PROVIDER_FUNCS.get(provider_name)
        if not func:
            continue
        try:
            return await func(prompt, max_tokens)
        except Exception as e:
            logger.warning(f"{provider_name} provayderida xatolik: {e}. Keyingisiga o'tilmoqda...")
            last_error = e
            continue
    raise RuntimeError(f"Barcha AI provayderlar ishlamadi. Oxirgi xato: {last_error}")


async def generate_reja(mavzu: str, reja_soni: int) -> list[str]:
    """
    Mavzu bo'yicha reja (bo'limlar ro'yxati) generatsiya qiladi.
    """
    prompt = (
        f"'{mavzu}' mavzusidagi mustaqil ish/referat uchun {reja_soni} ta "
        f"asosiy bo'limdan iborat reja tuzing. Kirish va Xulosa alohida "
        f"hisoblanmaydi, faqat asosiy {reja_soni} ta bo'lim nomini bering. "
        f"Har bir bo'lim nomini yangi qatordan, raqamlashtirib yozing. "
        f"Boshqa hech qanday izoh yozmang, faqat ro'yxat."
    )
    text = await ask_ai(prompt, max_tokens=500)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[:reja_soni]



    }