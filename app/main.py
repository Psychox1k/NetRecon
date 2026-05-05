import asyncio
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI

from app.tg_bot.main import bot, dp
from app.config.settings import settings
from app.routes.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    polling_task: asyncio.Task | None = None

    if settings.BOT_MODE == "polling":
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(
            dp.start_polling(
                bot,
                handle_signals=False,
            )
        )

    yield

    if polling_task is not None:
        polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await polling_task

    with suppress(Exception):
        await bot.session.close()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}
