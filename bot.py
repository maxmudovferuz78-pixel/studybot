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



