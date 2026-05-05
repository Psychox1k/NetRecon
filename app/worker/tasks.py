import asyncio
import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database.models import TargetModel, TargetStatus
from app.database import async_session

from app.scanner import scan_target
from app.services.scanner_service import ScanService
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def notify_user(
        chat_id: int,
        domain_name: str,
        scan_results=None,
        error: str = None
):
    if not chat_id:
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        if error:
            text = (
                f"❌ <b>Scan Error: {domain_name}</b>"
                f"\n\nReason: <code>{error}</code>"
            )
        else:
            ips_count = len(
                scan_results
            ) if isinstance(
                scan_results,
                list
            ) else len(scan_results.get("ips", []))
            text = (
                f"✅ <b>Scan Complete: {domain_name}</b>\n\n"
                f"🔍 IP addresses found: <b>{ips_count}</b>\n"
                f"💾 Data successfully saved."
                f" Go to the domain menu to view the results."
            )
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram notification to {chat_id}: {e}")
    finally:
        await bot.session.close()


async def process_scan_async(target_name: str, domain_name: str):
    scan_results = await scan_target(domain_name)

    async with async_session() as db:
        service = ScanService(db)
        await service.save_scan_results(target_name, domain_name, scan_results)

    return scan_results


async def fetch_active_targets_and_dispatch():

    async with async_session() as db:
        query = await db.execute(
            select(TargetModel)
            .where(TargetModel.status == TargetStatus.ACTIVE)
            .options(selectinload(TargetModel.domains))
        )
        active_targets = query.scalars().all()

        for target in active_targets:
            for domain in target.domains:
                scan_and_save_domain.delay(
                    target.name,
                    domain.domain_name,
                    None
                )


async def run_scan_workflow(
        target_name: str,
        domain_name: str,
        chat_id: int = None
):

    try:
        scan_results = await process_scan_async(target_name, domain_name)

        if chat_id:
            await notify_user(chat_id, domain_name, scan_results=scan_results)
    except Exception as e:
        logger.error(f"Error scanning {domain_name}: {e}")
        if chat_id:
            await notify_user(chat_id, domain_name, error=str(e))


@celery_app.task(name="scan_and_save_domain")
def scan_and_save_domain(
        target_name: str,
        domain_name: str,
        chat_id: int = None
):
    try:
        asyncio.run(run_scan_workflow(target_name, domain_name, chat_id))
    except Exception as e:
        logger.error(f"Critical error in scan task: {e}")


@celery_app.task(name="monitor_active_domains")
def monitor_active_domains():
    asyncio.run(fetch_active_targets_and_dispatch())
