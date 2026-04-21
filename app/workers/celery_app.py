from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,   # Fair task distribution
    task_acks_late=True,            # Ack only after completion
    result_expires=3600,            # Keep results for 1 hour
    task_routes={
        "app.workers.tasks.process_message_task": {"queue": "messages"},
    },
)
