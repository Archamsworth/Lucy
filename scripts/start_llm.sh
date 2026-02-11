#!/bin/bash

# Start llama.cpp server with Qwen2.5-3B

echo "🧠 Starting llama.cpp server with Qwen2.5-3B-Instruct..."

# Configuration
MODEL_PATH="${MODEL_PATH:-./qwen2.5-3b-instruct.gguf}"
CONTEXT_SIZE="${CONTEXT_SIZE:-4096}"
GPU_LAYERS="${GPU_LAYERS:-20}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Error: Model not found at $MODEL_PATH"
    echo "Please set MODEL_PATH environment variable or place model in current directory"
    exit 1
fi

# Check if llama.cpp server exists
if [ ! -f "./llama.cpp/server" ] && [ ! -f "./server" ]; then
    echo "❌ Error: llama.cpp server not found"
    echo "Please build llama.cpp first:"
    echo "  git clone https://github.com/ggerganov/llama.cpp"
    echo "  cd llama.cpp && make server"
    exit 1
fi

# Find server binary
SERVER_BIN=""
if [ -f "./llama.cpp/server" ]; then
    SERVER_BIN="./llama.cpp/server"
elif [ -f "./server" ]; then
    SERVER_BIN="./server"i

echo "Model: $MODEL_PATH"
echo "Context: $CONTEXT_SIZE"
echo "GPU Layers: $GPU_LAYERS"
echo "Host: $HOST:$PORT"
echo ""

# Start server
$SERVER_BIN \
    -m "$MODEL_PATH" \
    -c "$CONTEXT_SIZE" \
    -ngl "$GPU_LAYERS" \
    --host "$HOST" \
    --port "$PORT" \
    --n-predict 256 \
    --threads 4

echo "✨ Server started at http://$HOST:$PORT"