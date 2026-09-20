import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import BOT_TOKEN, REJA_OPTIONS, VAROQ_OPTIONS
from ai_service import generate_full_document
from doc_generator import build_document

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ---------------- FSM holatlari ----------------
class Order(StatesGroup):
    turi = State()          # Mustaqil ish / Referat
    mavzu = State()
    ism_familiya = State()
    universitet = State()
    guruh = State()
    oqituvchi = State()
    reja_soni = State()
    varoq_soni = State()


# ---------------- Klaviaturalar ----------------
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Yangi Mustaqil ish"), KeyboardButton(text="📄 Yangi Referat")],
        ],
        resize_keyboard=True,
    )


def reja_soni_kb() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(n), callback_data=f"reja:{n}")
        for n in REJA_OPTIONS
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def varoq_soni_kb() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=key, callback_data=f"varoq:{key}")
        for key in VAROQ_OPTIONS.keys()
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def bekor_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="bekor")]]
    )


# ---------------- Handlerlar ----------------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum!\n\n"
        "Ushbu bot orqali sun'iy intellekt yordamida:\n"
        "📘 — Mustaqil ishlar\n"
        "📄 — Referatlar\n\n"
        "tayyorlashingiz mumkin!\n\nHozircha bot bepul ishlamoqda 🎁",
        reply_markup=main_menu_kb(),
    )


@dp.message(F.text.in_(["📘 Yangi Mustaqil ish", "📄 Yangi Referat"]))
async def new_order(message: Message, state: FSMContext):
    turi = "Mustaqil ish" if "Mustaqil" in message.text else "Referat"
    await state.update_data(turi=turi)
    await state.set_state(Order.mavzu)
    await message.answer(
        f"{turi} uchun mavzu nomini to'liq va bexato kiriting:",
        reply_markup=bekor_kb(),
    )


@dp.message(Order.mavzu)
async def get_mavzu(message: Message, state: FSMContext):
    await state.update_data(mavzu=message.text.strip())
    await state.set_state(Order.ism_familiya)
    await message.answer(
        "Familiya va ismingizni kiriting.\nMisol: Salimov Bahodir",
        reply_markup=bekor_kb(),
    )


@dp.message(Order.ism_familiya)
async def get_ism(message: Message, state: FSMContext):
    await state.update_data(ism_familiya=message.text.strip())
    await state.set_state(Order.universitet)
    await message.answer(
        "Universitet nomini kiriting:\n"
        "Misol: TOSHKENT DAVLAT AXBOROT TEXNOLOGIYALARI UNIVERSITETI",
        reply_markup=bekor_kb(),
    )


@dp.message(Order.universitet)
async def get_universitet(message: Message, state: FSMContext):
    await state.update_data(universitet=message.text.strip())
    await state.set_state(Order.guruh)
    await message.answer(
        "Guruh nomini kiriting:\nMisol: 072-24 SAXo'",
        reply_markup=bekor_kb(),
    )


@dp.message(Order.guruh)
async def get_guruh(message: Message, state: FSMContext):
    await state.update_data(guruh=message.text.strip())
    await state.set_state(Order.oqituvchi)
    await message.answer(
        "O'qituvchi familiya ismini kiriting:\nMisol: Sobirov Doniyor",
        reply_markup=bekor_kb(),
    )


@dp.message(Order.oqituvchi)
async def get_oqituvchi(message: Message, state: FSMContext):
    await state.update_data(oqituvchi=message.text.strip())
    await state.set_state(Order.reja_soni)
    await message.answer(
        "Reja nechta bo'limdan iborat bo'lsin?",
        reply_markup=reja_soni_kb(),
    )


@dp.callback_query(F.data.startswith("reja:"), Order.reja_soni)
async def get_reja_soni(callback: CallbackQuery, state: FSMContext):
    reja_soni = int(callback.data.split(":")[1])
    await state.update_data(reja_soni=reja_soni)
    await state.set_state(Order.varoq_soni)
    await callback.message.edit_text(f"Reja bo'limlari soni: {reja_soni} ✅")
    await callback.message.answer(
        "Hujjat necha varoqdan iborat bo'lsin?",
        reply_markup=varoq_soni_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("varoq:"), Order.varoq_soni)
async def get_varoq_soni(callback: CallbackQuery, state: FSMContext):
    varoq_key = callback.data.split(":")[1]
    await state.update_data(varoq_key=varoq_key)
    await callback.message.edit_text(f"Hajmi: {varoq_key} varoq ✅")
    await callback.answer()

    data = await state.get_data()
    await callback.message.answer(
        "♻️ Hujjat yaratilmoqda...\n⏱ Vaqt: 1-3 daqiqa\nJarayon yakunlangach sizga hujjat yuboriladi."
    )

    varoq_config = VAROQ_OPTIONS[varoq_key]
    chars_per_section = varoq_config["chars_per_section"]

    try:
        content = await generate_full_document(
            mavzu=data["mavzu"],
            reja_soni=data["reja_soni"],
            chars_per_section=chars_per_section,
        )

        file_id = str(uuid.uuid4())
        filepath = build_document(
            turi=data["turi"],
            mavzu=data["mavzu"],
            ism_familiya=data["ism_familiya"],
            universitet=data["universitet"],
            guruh=data["guruh"],
            oqituvchi=data["oqituvchi"],
            content=content,
            file_id=file_id,
        )

        await callback.message.answer_document(
            FSInputFile(filepath, filename=f"{data['mavzu']}.docx"),
            caption="✅ Jarayon yakunlandi. Sizga hujjat yuborildi.",
        )
    except Exception as e:
        logging.exception("Hujjat generatsiyasida xatolik")
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring."
        )
    finally:
        await state.clear()


@dp.callback_query(F.data == "bekor")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu_kb())
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
