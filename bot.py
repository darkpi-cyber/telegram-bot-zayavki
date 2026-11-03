"""Telegram-бот для приёма заявок (aiogram 3).

Меню: Услуги, Цены, Оставить заявку, Контакты.
Заявка (имя -> телефон -> комментарий) уходит владельцу в личку.
"""
import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Моя студия")

SERVICES = (
    "Наши услуги:\n"
    "• Консультация\n"
    "• Базовый пакет\n"
    "• Расширенный пакет\n"
)
PRICES = (
    "Цены:\n"
    "• Консультация — 1 000 ₽\n"
    "• Базовый пакет — 5 000 ₽\n"
    "• Расширенный пакет — 12 000 ₽\n"
)
CONTACTS = "Контакты:\nТелефон: +7 900 000-00-00\nГрафик: пн–пт, 10:00–19:00"

BTN_SERVICES = "Услуги"
BTN_PRICES = "Цены"
BTN_APPLY = "Оставить заявку"
BTN_CONTACTS = "Контакты"
BTN_CANCEL = "Отмена"

PHONE_RE = re.compile(r"^\+?\d[\d\s\-()]{9,17}$")

router = Router()


class Application(StatesGroup):
    name = State()
    phone = State()
    comment = State()


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SERVICES), KeyboardButton(text=BTN_PRICES)],
            [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CONTACTS)],
        ],
        resize_keyboard=True,
    )


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"Здравствуйте! Это бот «{BUSINESS_NAME}».\nВыберите пункт меню:",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_CANCEL)
@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())


@router.message(F.text == BTN_SERVICES)
async def services(message: Message) -> None:
    await message.answer(SERVICES)


@router.message(F.text == BTN_PRICES)
async def prices(message: Message) -> None:
    await message.answer(PRICES)


@router.message(F.text == BTN_CONTACTS)
async def contacts(message: Message) -> None:
    await message.answer(CONTACTS)


@router.message(F.text == BTN_APPLY)
async def apply_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Application.name)
    await message.answer("Как к вам обращаться?", reply_markup=cancel_menu())


@router.message(Application.name, F.text)
async def apply_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not 2 <= len(name) <= 50:
        await message.answer("Введите имя от 2 до 50 символов.")
        return
    await state.update_data(name=name)
    await state.set_state(Application.phone)
    await message.answer("Укажите номер телефона:")


@router.message(Application.phone, F.text)
async def apply_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    if not PHONE_RE.match(phone):
        await message.answer("Не похоже на номер. Пример: +7 900 123-45-67")
        return
    await state.update_data(phone=phone)
    await state.set_state(Application.comment)
    await message.answer("Коротко опишите, что вам нужно:")


@router.message(Application.comment, F.text)
async def apply_comment(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user and user.username else "нет username"
    text = (
        "Новая заявка\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Комментарий: {message.text.strip()}\n"
        f"Telegram: {username} (id {user.id if user else '?'})"
    )

    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text)
        except Exception:
            logging.exception("Не удалось отправить заявку администратору")
    else:
        logging.warning("ADMIN_ID не задан, заявка только в лог:\n%s", text)

    await message.answer(
        "Спасибо! Заявка принята, мы свяжемся с вами.", reply_markup=main_menu()
    )


@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Выберите пункт меню ниже.", reply_markup=main_menu())


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("Не задан BOT_TOKEN. Скопируйте .env.example в .env и впишите токен.")
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
