import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models import TargetModel, TargetStatus
from database.session_postgresql import AsyncPostgresqlSessionLocal as async_session

from scanner.core import scan_target
from services.scanner_service import ScanService
from worker import celery_app

async def process_scan_async(target_name: str, domain_name: str):
    scan_results = await scan_target(domain_name)

    async with async_session() as db:
        service = ScanService(db)
        await service.save_scan_results(target_name, domain_name, scan_results)

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
                scan_and_save_domain.delay(target.name, domain.domain_name, 0)

@celery_app.task(name="scan_and_save_domain")
def scan_and_save_domain(target_name: str, domain_name: str, chat_id):

    asyncio.run(process_scan_async(target_name, domain_name))
    # send_telegram_message(chat_id, f"✅ Scanning {domain_name} successfully completed and saved to Database!")

@celery_app.task(name="monitor_active_domains")
def monitor_active_domains():
    asyncio.run(fetch_active_targets_and_dispatch())