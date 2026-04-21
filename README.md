# 🤖 AI Automation Backend Platform

A production-ready hybrid AI backend system that automatically routes customer
messages through the most cost-effective AI layer — cutting OpenAI costs by 85–90%.

---

## 🧩 Problem It Solves

| Problem | This Platform |
|---|---|
| Delayed customer responses | Sub-second template replies |
| High OpenAI API costs | 3-tier routing (Template → Local → OpenAI) |
| No scalable async processing | Celery + Redis workers |
| Repetitive manual replies | 7+ built-in response templates |
| No WhatsApp / email automation | Native integrations included |

---

## 🏗 Architecture

```
Client Request
      ↓
API Gateway (FastAPI)
      ↓
Rate Limiter (Redis — 60 req/min per sender)
      ↓
Decision Engine
  ├── 1. Redis Cache        → instant if seen before
  ├── 2. Template Engine    → regex match, confidence ≥ 0.85 (FREE)
  ├── 3. Local LLM (Ollama) → on-premise Mistral, confidence ≥ 0.70 (~$0)
  └── 4. OpenAI API         → fallback only (pay per token)
      ↓
Celery Queue (async)
      ↓
Workers (process + dispatch)
      ↓
Integration Layer
  ├── WhatsApp Cloud API
  └── SMTP Email
      ↓
PostgreSQL (logs) + Redis (cache)
```

---

## 🚀 Quick Start

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Celery Monitor | http://localhost:5555 |

---

## 📡 API Reference

### Submit a Message
```http
POST /api/v1/messages
Content-Type: application/json

{
  "channel": "api",          // "api" | "whatsapp" | "email"
  "sender_id": "user_123",
  "content": "hello, I need help with pricing",
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "uuid-here",
  "task_id": "celery-task-id",
  "estimated_response_time": 5
}
```

### Health Check
```http
GET /api/v1/health
```

### Analytics Summary
```http
GET /api/v1/analytics/summary
```
Returns routing breakdown, avg response time, and estimated cost saved.

### WhatsApp Webhook
```http
GET  /api/v1/webhooks/whatsapp   # Verification
POST /api/v1/webhooks/whatsapp   # Incoming messages
```

---

## 💰 Cost Optimization

With default thresholds (template ≥ 0.85, local LLM ≥ 0.70):

| Tier | Typical % | Cost |
|---|---|---|
| Template | ~60% | $0 |
| Local LLM (Mistral) | ~25% | ~$0 |
| OpenAI | ~15% | ~$0.002/msg |

**Estimated saving vs pure OpenAI: 85%+**

---

## ⚙️ Configuration


Key settings:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI key (fallback only) |
| `WHATSAPP_TOKEN` | — | WhatsApp Business token |
| `LOCAL_LLM_MODEL` | `mistral` | Ollama model name |
| `TEMPLATE_CONFIDENCE_THRESHOLD` | `0.85` | Min score for template routing |
| `LOCAL_LLM_CONFIDENCE_THRESHOLD` | `0.70` | Min score for local LLM routing |
| `RATE_LIMIT_PER_MINUTE` | `60` | Requests per sender per minute |

---


## 📁 Project Structure

```
ai_automation_platform/
├── app/
│   ├── main.py                    # FastAPI app factory
│   ├── api/routes/
│   │   ├── messages.py            # POST /messages
│   │   ├── webhooks.py            # WhatsApp webhook
│   │   ├── health.py              # GET /health
│   │   └── analytics.py          # GET /analytics/summary
│   ├── core/
│   │   ├── config.py              # All settings (pydantic-settings)
│   │   ├── database.py            # SQLAlchemy async engine
│   │   ├── redis_client.py        # Redis async client
│   │   └── logging.py             # JSON structured logging
│   ├── engine/
│   │   ├── decision_engine.py     # ⭐ Core routing logic
│   │   ├── template_engine.py     # Regex pattern matching
│   │   ├── local_llm.py           # Ollama client
│   │   └── openai_client.py       # OpenAI fallback
│   ├── integrations/
│   │   ├── whatsapp.py            # WhatsApp Cloud API
│   │   └── email_client.py        # SMTP async email
│   ├── workers/
│   │   ├── celery_app.py          # Celery configuration
│   │   └── tasks.py               # Async processing tasks
│   ├── models/
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── message_log.py         # SQLAlchemy ORM model
│   └── utils/
│       └── rate_limiter.py        # Redis rate limiter
├── tests/
│   ├── test_decision_engine.py
│   ├── test_api.py
│   └── test_template_engine.py
├── docker/
│   └── docker-compose.yml         # 6-service stack
├── scripts/
│   └── start.sh                   # One-command setup
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## 🛠 Tech Stack

- **FastAPI** — async REST API
- **Celery + Redis** — distributed task queue
- **PostgreSQL + SQLAlchemy** — persistent storage
- **Ollama (Mistral)** — local LLM, zero cost
- **OpenAI GPT-3.5** — cloud fallback
- **WhatsApp Cloud API** — messaging integration
- **aiosmtplib** — async email
- **Docker Compose** — one-command deployment
