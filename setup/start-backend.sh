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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please copy .env.example to .env and add your OpenAI API key"
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OpenAI API key may not be configured properly"
    echo "   Please ensure OPENAI_API_KEY is set in .env file"
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
