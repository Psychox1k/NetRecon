from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm import state
from aiogram.types import Message

from app.tg_bot.keyboards.reply import get_main_menu
from app.tg_bot.states import AddTarget

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"HI, <b>{message.from_user.first_name}</b>!\n"
        f"I am bot for domain scanning. Choose option below menu 👇.",
        reply_markup = get_main_menu()
    )

@router.message(F.text == "ℹ️ Help")
async def add_domain_start(message: Message):
    await message.answer("HELLO it\' s service for scanning domain ")
