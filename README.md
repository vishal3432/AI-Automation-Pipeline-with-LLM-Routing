# AI Automation Pipeline

It's an AI-powered customer support automation backend. When a customer sends a message (via WhatsApp, email, or API), the system automatically replies using the cheapest AI option available:


Template Engine (free) — if the message matches a known pattern (greeting, pricing, refund, hours, etc.), it instantly returns a pre-written reply

Local LLM via Ollama (near-free) — if no template matches, it sends the message to a self-hosted Mistral model running on your own server

OpenAI GPT (paid fallback) — only if the local LLM is unavailable or low confidence, it escalates to ChatGPT


Every response is cached in Redis so repeated questions cost nothing. All messages are logged to PostgreSQL and you can view routing stats (how many went to template vs local vs OpenAI, cost saved) via /api/v1/analytics/summary.
The stack is: FastAPI (API) + Celery (async task queue) + Redis (cache + queue) + PostgreSQL (logs) + Ollama (local AI) — all running in Docker.

Inshort, Intelligent backend system for cost-optimized AI request processing using multi-tier LLM routing (Cache → Templates → Local LLM → OpenAI)

---

# What is This?

An AI-powered automated reply system that instantly responds to customer messages on WhatsApp, Email, and API — without any human involvement.

---

# How It Works

Every incoming message is routed through 3 AI layers, always picking the cheapest option first:
Customer Message
      ↓
1. Template Match  →  instant reply, zero cost    (greetings, pricing, refunds...)
      ↓ no match
2. Local AI (Mistral via Ollama)  →  free reply, runs on your server
      ↓ low confidence or offline
3. OpenAI GPT  →  smartest reply, ~$0.002 per message

### Note - Responses are cached in Redis so repeated questions cost nothing twice.

---

# What You Do

Fill in .env with your API keys
Run ./scripts/start.sh
Point your WhatsApp webhook to your server

### That's it. Everything else is automatic.

| Channel | How |
|---------|-----|
| WhatsApp | Meta webhook → fully automatic |
| Email | Via SMTP — triggered by API call |
| API | Direct POST from your app or website |

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


## Key Insight

> Designed as a backend-first AI automation system with strong focus on scalability, async processing, and cost efficiency.

---
