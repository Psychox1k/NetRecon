import asyncio
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI

from app.tg_bot.main import bot, dp
from app.config.settings import settings
from app.routes.api import api_router

# --- Swagger UI Description ---
description = """
**NetScan API** is the core of the automated infrastructure scanning system. 🚀

## Features:
* **Targets** - Manage scan targets (projects/infrastructures).
* **Domains & IPs** - Keep track of domain names and associated IP addresses.
* **Ports & SSL** - Results of open port scans and SSL certificate parsing.
"""

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

    # Bot graceful shutdown logic
    if polling_task is not None:
        polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await polling_task

    with suppress(Exception):
        await bot.session.close()

# --- FastAPI Initialization with documentation settings ---
app = FastAPI(
    title="NetScan API",
    description=description,
    version="1.0.0",
    contact={
        "name": "ScanDomain Admin",
    },
    lifespan=lifespan
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Healthcheck"], summary="API Status Check")
async def root():
    """
    Base endpoint to verify that the server is up and running.
    """
    return {"status": "ok", "message": "NetScan API is running!"}