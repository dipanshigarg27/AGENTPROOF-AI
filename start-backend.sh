#!/bin/bash
# AgentProof AI — Start Backend
# Run from the project root: ./start-backend.sh

set -e
echo "🚀 Starting AgentProof AI Backend..."
echo ""

BACKEND_DIR="$(dirname "$0")/backend"
cd "$BACKEND_DIR"

# Create venv if needed
if [ ! -d "venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Check .env exists
if [ ! -f ".env" ]; then
  echo "⚠️  No .env file found. Copying from template..."
  cp "../.env.example" ".env"
  echo "⚠️  Please edit backend/.env and add your API keys."
  echo "   TAVILY_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY"
  echo ""
fi

echo "✅ Backend starting at http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
