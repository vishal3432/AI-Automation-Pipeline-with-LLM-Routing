# AI Automation Pipeline

 Intelligent backend system for cost-optimized AI request processing using multi-tier LLM routing (Cache → Templates → Local LLM → OpenAI).

---

##  Key Highlights

* **85–90% cost reduction** using intelligent routing
* **Sub-second responses** via caching & templates
* **Hybrid AI system** (Local LLM + OpenAI fallback)
* **Async processing** with Celery + Redis
* **Production-ready architecture (Dockerized)**

---

##  Problem → Solution

| Problem                | Solution           |
| ---------------------- | ------------------ |
| High OpenAI costs      | Multi-tier routing |
| Slow response times    | Cache + templates  |
| Blocking APIs          | Async workers      |
| Repetitive queries     | Template engine    |
| Integration complexity | Unified backend    |

---

## How It Works

```text
Request → FastAPI → Redis → Decision Engine
         → Cache / Template / Local LLM / OpenAI
         → Celery → Worker → Response
```

---

## Cost Optimization

| Tier      | Usage | Cost |
| --------- | ----- | ---- |
| Cache     | ~60%  | Free |
| Templates | ~20%  | Free |
| Local LLM | ~15%  | ~$0  |
| OpenAI    | ~5%   | Paid |

👉 **85%+ cost savings vs direct OpenAI**

---

##  API Example

```http
POST /api/v1/messages
```

```json
{
  "content": "pricing details",
  "sender_id": "user_1"
}
```

---

##  Tech Stack

* FastAPI
* Redis
* Celery
* PostgreSQL
* Ollama (Mistral)
* OpenAI API
* Docker

---

## Project Structure

```bash
app/
├── api/
├── core/
├── engine/
├── integrations/
├── workers/
├── models/
└── utils/
```

---

## Run Locally

```bash
docker-compose up --build
```

---

## Features

* Multi-tier AI routing
* Async task processing
* Rate limiting
* Structured logging
* WhatsApp + Email integration

---

## Future Work

* Workflow builder UI
* Analytics dashboard
* Multi-tenant SaaS

---

## Key Insight

> Designed as a backend-first AI automation system with strong focus on scalability, async processing, and cost efficiency.

---
