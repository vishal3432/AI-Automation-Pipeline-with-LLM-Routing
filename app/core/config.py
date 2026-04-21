from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AI Automation Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@postgres:5432/ai_platform"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Local LLM (Ollama)
    LOCAL_LLM_URL: str = "http://ollama:11434"
    LOCAL_LLM_MODEL: str = "mistral"

    # WhatsApp
    WHATSAPP_API_URL: str = ""
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    # BUG FIX: App Secret is needed for HMAC webhook signature validation —
    # separate from the verify token. Set this in your .env file.
    WHATSAPP_APP_SECRET: str = ""

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Decision thresholds
    TEMPLATE_CONFIDENCE_THRESHOLD: float = 0.85
    LOCAL_LLM_CONFIDENCE_THRESHOLD: float = 0.70

    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
