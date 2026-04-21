from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.models.schemas import IncomingMessage, MessageResponse
from app.utils.rate_limiter import RateLimiter
from app.workers.tasks import process_message_task
import uuid

router = APIRouter()
rate_limiter = RateLimiter()


@router.post("/messages", response_model=MessageResponse, summary="Submit a message for AI processing")
async def receive_message(
    payload: IncomingMessage,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    Accept an incoming message from any channel (WhatsApp, email, API),
    apply rate limiting, then dispatch async processing via Celery.
    """
    is_allowed = await rate_limiter.check(payload.sender_id, redis)
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before sending another message."
        )

    message_id = str(uuid.uuid4())

    task = process_message_task.delay(
        message_id=message_id,
        channel=payload.channel.value,
        sender_id=payload.sender_id,
        content=payload.content,
        metadata=payload.metadata or {},
    )

    return MessageResponse(
        success=True,
        message_id=message_id,
        task_id=task.id,
        estimated_response_time=5,
    )


@router.get("/messages/{message_id}", summary="Get message processing status")
async def get_message_status(message_id: str, redis=Depends(get_redis)):
    status = await redis.get(f"msg_status:{message_id}")
    if not status:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message_id": message_id, "status": status}
