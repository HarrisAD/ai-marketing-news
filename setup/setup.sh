#!/bin/bash

# AI Marketing News System - Setup Script
# Run this script to set up the complete system

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Setting up AI Marketing News System..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    echo "   Please install Node.js which includes npm"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend setup
echo "🐍 Setting up Python backend..."
cd "$PROJECT_ROOT/backend"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || echo "Note: Virtual environment not activated"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_actual_api_key_here"
    echo ""
    echo "   Get your API key at: https://platform.openai.com/api-keys"
    echo ""
fi

# Create data directories
mkdir -p data logs

cd "$PROJECT_ROOT"

# Frontend setup
echo "📱 Setting up React frontend..."
cd "$PROJECT_ROOT/frontend"

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd "$PROJECT_ROOT"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start the backend:"
echo "   cd backend/src && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For detailed instructions, see README.md"
