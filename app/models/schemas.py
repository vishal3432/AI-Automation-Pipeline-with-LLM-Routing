from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field

class ChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    API = "api"


class RoutingStrategy(str, Enum):
    TEMPLATE = "template"
    LOCAL_LLM = "local_llm"
    OPENAI = "openai"


class IncomingMessage(BaseModel):
    channel: ChannelType
    sender_id: str
    sender_name: Optional[str] = None
    content: str
    metadata: Optional[dict] = Field(default_factory=dict)


class ProcessedMessage(BaseModel):
    message_id: str
    original_content: str
    response: str
    routing_strategy: RoutingStrategy
    confidence_score: float
    processing_time_ms: float
    timestamp: datetime


class MessageResponse(BaseModel):
    success: bool
    message_id: str
    task_id: Optional[str] = None
    estimated_response_time: int = 5  # seconds


class AnalyticsReport(BaseModel):
    total_messages: int
    template_hits: int
    local_llm_hits: int
    openai_hits: int
    avg_response_time_ms: float
    cost_saved_usd: float
