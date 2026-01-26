from apscheduler.schedulers.background import BackgroundScheduler
from .config import settings
from .db import SessionLocal
from .deps import get_flowshadow_client, get_deepsoc_client
from .services.sync import run_sync_once

scheduler = BackgroundScheduler()

def start_scheduler() -> None:
    if not settings.sync_enabled:
        return

    def job():
        db = SessionLocal()
        try:
            fs = get_flowshadow_client()
            ds = get_deepsoc_client()
            run_sync_once(
                db, fs, ds,
                batch_size=settings.sync_batch_size,
                lookback_seconds=settings.sync_lookback_seconds,
                max_retries=settings.sync_max_retries,
            )
        finally:
            db.close()

    scheduler.add_job(
        job,
        "interval",
        seconds=settings.sync_interval_seconds,
        id="sync_job",
        replace_existing=True,
    )
    scheduler.start()
