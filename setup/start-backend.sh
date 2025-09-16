#!/bin/bash

# Start the AI Marketing News Backend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 Starting AI Marketing News Backend..."

cd "$PROJECT_ROOT/backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Ensure .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "ℹ️  Creating .env from template..."
        cp .env.example .env
    else
        echo "❌ .env.example not found. Please run setup first."
        exit 1
    fi
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OpenAI API key is not configured yet. Use the dashboard to paste it before generating stories."
fi

# Create data directories
mkdir -p data logs

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
