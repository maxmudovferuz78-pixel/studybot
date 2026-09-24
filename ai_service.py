"""
AI orqali mustaqil ish / referat matnini generatsiya qilish.

Uchta provayder qo'llab-quvvatlanadi: OpenAI, Gemini, Claude.
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
_gemini_configured = False

if OPENAI_API_KEY:
    from openai import AsyncOpenAI
    _openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

if ANTHROPIC_API_KEY:
    from anthropic import AsyncAnthropic
    _anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_configured = True


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
    if not _gemini_configured:
        raise RuntimeError("Gemini kaliti sozlanmagan")
    import google.generativeai as genai
    model = genai.GenerativeModel(GEMINI_MODEL)
    # Gemini SDK sinxron — alohida threadda ishlatib event loopni bloklamaymiz
    response = await asyncio.to_thread(
        model.generate_content,
        prompt,
        generation_config={"temperature": 0.7, "max_output_tokens": max_tokens},
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
    Masalan: ["Kirish", "1. ...", "2. ...", "Xulosa"]
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
    return await ask_ai(prompt, max_tokens=2000)


async def generate_full_document(mavzu: str, reja_soni: int, chars_per_section: int) -> dict:
    """
    Butun hujjatni generatsiya qiladi: reja, kirish, har bir bo'lim, xulosa.
    Bo'limlarni parallel generatsiya qilib vaqtni tejaydi.
    """
    reja = await generate_reja(mavzu, reja_soni)

    tasks = [generate_section(mavzu, "", chars_per_section, is_kirish=True)]
    for bolim in reja:
        tasks.append(generate_section(mavzu, bolim, chars_per_section))
    tasks.append(generate_section(mavzu, "", chars_per_section, is_xulosa=True))

    results = await asyncio.gather(*tasks)

    return {
        "kirish": results[0],
        "bolimlar": list(zip(reja, results[1:-1])),
        "xulosa": results[-1],
    }