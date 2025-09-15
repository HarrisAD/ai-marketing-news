#!/bin/bash

echo "============================================"
echo "  Starting AI Marketing News System"
echo "============================================"
echo

# Check if .env file exists and has API key
if [ ! -f "backend/.env" ]; then
    echo "ERROR: Configuration file not found!"
    echo "Please run setup.sh first"
    exit 1
fi

if grep -q "your_openai_api_key_here" backend/.env; then
    echo "ERROR: OpenAI API key not configured!"
    echo
    echo "Please edit backend/.env and add your OpenAI API key"
    echo "Get your key from: https://platform.openai.com/api-keys"
    echo
    exit 1
fi

echo "Starting backend server..."
cd backend/src
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

sleep 3

echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

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