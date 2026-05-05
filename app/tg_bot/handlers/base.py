from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
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


@router.message(F.text == "ℹ️ About")
@router.message(Command("about"))
async def show_about_info(message: types.Message):
    about_text = (
        "<b>🚀 ScanDomen</b> — a cutting-edge infrastructure monitoring tool.\n\n"
        "Our philosophy: <i>speed, reliability, and absolutely zero legacy.</i>\n\n"
        "<b>⚙️ Under the hood:</b>\n"
        "• Fully asynchronous architecture\n"
        "• Isolated background workers\n"
        "• Clean, modern tech stack\n\n"
        "We automate the scanning routine, giving you a lightning-fast "
        "interface right in Telegram. No compromises—just modern solutions "
        "for real tasks."
    )

    await message.answer(
        text=about_text,
        parse_mode="HTML"  # Required for <b> and <i> tags to work
    )