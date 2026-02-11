#!/bin/bash

# Start Lucy AI Companion Backend

echo "🚀 Starting Lucy AI Companion Backend..."

# Check if llama.cpp server is running
echo "Checking llama.cpp server..."
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "⚠️  Warning: llama.cpp server not running on port 8001"
    echo "Please start it first with:"
    echo "./llama.cpp/server -m qwen2.5-3b-instruct.gguf -c 4096 -ngl 20 --host 0.0.0.0 --port 8001"
    echo ""
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start FastAPI server
echo "✨ Starting FastAPI server on http://localhost:8000"
python main.py
