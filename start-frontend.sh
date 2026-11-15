#!/bin/bash
# AgentProof AI — Start Frontend
# Run from the project root: ./start-frontend.sh

set -e
echo "🎨 Starting AgentProof AI Frontend..."
echo ""

FRONTEND_DIR="$(dirname "$0")/frontend"
cd "$FRONTEND_DIR"

# Install if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing npm packages..."
  npm install
fi

echo "✅ Frontend starting at http://localhost:5173"
echo ""

npm run dev
