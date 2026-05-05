from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="🎯 My targets")
    builder.button(text="➕ Add target")
    builder.button(text="ℹ️ About")

    builder.adjust(2, 1)

    return builder.as_markup(resize_keyboard=True)

def get_target_create_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="Add domain to scan")
    builder.button(text="Back to Menu")
    return builder.as_markup(resize_keyboard=True)


def get_cancel_rkb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Cancel"))
    return builder.as_markup(resize_keyboard=True)