import asyncio
import threading
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI

from app.tg_bot.main import bot, dp
from app.config.settings import settings

from app.routes.target import router as target_router
from app.routes.ip import router as ip_router
from app.routes.ssl_certificate import router as ssl_certificate_router
from app.routes.domain import router as domain_router
from app.routes.port import router as port_router


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

app.include_router(target_router)
app.include_router(ip_router)
app.include_router(ssl_certificate_router)
app.include_router(domain_router)
app.include_router(port_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
