#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$PROJECT_ROOT"

echo "============================================"
echo "  Starting AI Marketing News System"
echo "============================================"
echo

# Ensure .env exists
if [ ! -f "backend/.env" ]; then
    echo "No backend/.env found. Creating one from backend/.env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "➡️  backend/.env created. You can paste your OpenAI API key via the dashboard once it loads."
    else
        echo "ERROR: backend/.env.example not found. Please re-run setup first."
        exit 1
    fi
fi

# Warn if API key placeholder still present
if grep -q "your_openai_api_key_here" backend/.env; then
    echo "⚠️  OpenAI API key not configured yet. You'll be prompted on the dashboard to paste it before generating stories."
fi

echo "Starting backend server..."
cd "$PROJECT_ROOT/backend/src"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

sleep 3

echo "Starting frontend server..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

sleep 5

echo
echo "============================================"
echo "  AI Marketing News System is Running!"
echo "============================================"
echo
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo
echo "Opening your AI news system..."
echo

# Try to open the frontend in the default browser
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
fi

echo "Press Ctrl+C to stop the system..."

# Wait for user to stop
trap "echo; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

wait
