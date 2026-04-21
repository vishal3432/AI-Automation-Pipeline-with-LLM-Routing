set -e

echo " AI Automation Backend Platform — Setup"
echo "==========================================="

# 1. Copy env file if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — please fill in your credentials"
else
  echo ".env already exists"
fi

# 2. Start all Docker services
echo ""
echo " Starting Docker services..."
docker compose -f docker/docker-compose.yml up -d --build

# 3. Wait for Postgres to be ready
echo ""
echo " Waiting for PostgreSQL..."
until docker exec ai_platform_postgres pg_isready -U user -d ai_platform > /dev/null 2>&1; do
  sleep 1
done
echo " PostgreSQL is ready"

# 4. Pull Mistral model into Ollama
echo ""
echo " Pulling Mistral model into Ollama (this may take a few minutes)..."
docker exec ai_platform_ollama ollama pull mistral || echo " Ollama model pull failed — you can do this manually later"

echo ""
echo "✅ All services started!"
echo ""
echo " API:         http://localhost:8000"
echo " API Docs:    http://localhost:8000/docs"
echo " Flower:      http://localhost:5555"
echo ""
echo "Test with:"
echo "  curl -X POST http://localhost:8000/api/v1/messages \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"channel\": \"api\", \"sender_id\": \"user1\", \"content\": \"hello\"}'"
