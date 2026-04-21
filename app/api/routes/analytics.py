from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()


@router.get("/analytics/summary", summary="Get routing & cost analytics")
async def get_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT
            COUNT(*)                                                        AS total,
            SUM(CASE WHEN routing_strategy = 'template'  THEN 1 ELSE 0 END) AS template_hits,
            SUM(CASE WHEN routing_strategy = 'local_llm' THEN 1 ELSE 0 END) AS local_llm_hits,
            SUM(CASE WHEN routing_strategy = 'openai'    THEN 1 ELSE 0 END) AS openai_hits,
            AVG(processing_time_ms)                                         AS avg_time_ms
        FROM message_logs
    """))
    row = result.fetchone()

    total       = row.total or 0
    openai_hits = row.openai_hits or 0
    # Each non-OpenAI message saves ~$0.002 (avg OpenAI cost)
    cost_saved  = (total - openai_hits) * 0.002

    return {
        "total_messages":       total,
        "template_hits":        row.template_hits  or 0,
        "local_llm_hits":       row.local_llm_hits or 0,
        "openai_hits":          openai_hits,
        "template_ratio":       round((row.template_hits  or 0) / max(total, 1), 3),
        "local_llm_ratio":      round((row.local_llm_hits or 0) / max(total, 1), 3),
        "openai_ratio":         round(openai_hits            / max(total, 1), 3),
        "avg_response_time_ms": round(row.avg_time_ms or 0, 2),
        "cost_saved_usd":       round(cost_saved, 4),
    }
