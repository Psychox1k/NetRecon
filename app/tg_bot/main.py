from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config.settings import settings

from app.tg_bot.handlers.base import router as base_router
from app.tg_bot.handlers.targets import router as target_router

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

dp = Dispatcher()

dp.include_router(base_router)
dp.include_router(target_router)