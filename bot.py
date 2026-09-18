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


