#!/bin/bash
# Quick Start Script for AI Resume Analyzer

set -e

echo "AI Resume Analyzer - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo "PLEASE UPDATE backend/.env with your API key and LLM_PROVIDER"
    exit 1
fi

read_env() {
    local key="$1"
    local value
    value="$(grep -E "^${key}=" backend/.env | tail -n 1 | cut -d= -f2- | tr -d '\r')"
    echo "$value"
}

LLM_PROVIDER="$(read_env LLM_PROVIDER)"
ANTHROPIC_API_KEY="$(read_env ANTHROPIC_API_KEY)"
GROQ_API_KEY="$(read_env GROQ_API_KEY)"
PORT="$(read_env PORT)"

LLM_PROVIDER="${LLM_PROVIDER:-claude}"
PORT="${PORT:-8000}"

if [ "$LLM_PROVIDER" = "groq" ]; then
    if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
        echo "ERROR: GROQ_API_KEY is missing or still a placeholder in backend/.env while LLM_PROVIDER=groq"
        exit 1
    fi
else
    if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_api_key_here" ]; then
        echo "ERROR: ANTHROPIC_API_KEY is missing or still a placeholder in backend/.env while LLM_PROVIDER=$LLM_PROVIDER"
        exit 1
    fi
fi

# Activate venv if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ -f backend/venv/Scripts/activate ]; then
        # Git Bash / Windows layout
        source backend/venv/Scripts/activate
    elif [ -f backend/venv/bin/activate ]; then
        # Linux/macOS layout
        source backend/venv/bin/activate
    else
        echo "ERROR: Virtual environment not found at backend/venv"
        echo "Create it with: python -m venv backend/venv"
        exit 1
    fi
fi

echo "Starting AI Resume Analyzer..."
echo "================================"
echo ""
echo "Server will be available at: http://localhost:${PORT}"
echo "Web UI: http://localhost:${PORT}"
echo "API Docs: http://localhost:${PORT}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python run.py
