from celery import Celery
from celery.schedules import crontab

from app.config import settings
from celery.app import Celery


celery_app = Celery(
    "scanner_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "monitor_active_domains_every_15_mins": {
        "task": "monitor_active_domains",
        "schedule": crontab(minute="*/15"),
    }
}
celery_app.autodiscover_tasks(["app.worker"])