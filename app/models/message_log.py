from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = Column(String, nullable=False)
    sender_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    response = Column(String, nullable=False)
    routing_strategy = Column(String, nullable=False, index=True)
    confidence_score = Column(Float, default=0.0)
    processing_time_ms = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
