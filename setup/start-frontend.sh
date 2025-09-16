#!/bin/bash

# Start the AI Marketing News Frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 Starting AI Marketing News Frontend..."

cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting React development server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"

npm run dev
