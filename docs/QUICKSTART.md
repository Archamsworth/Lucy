# 🚀 Quick Start Guide - Lucy AI Companion

Get Lucy up and running in 15 minutes!

## Overview

This guide will help you quickly set up and test Lucy. For detailed documentation, see:
- [SETUP.md](SETUP.md) - Full setup instructions
- [API.md](API.md) - API documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

## What You'll Need

✅ **Already Have:**
- Qwen2.5-3B-Instruct GGUF model
- VRM avatar model

📥 **Need to Install:**
- Python 3.10+
- llama.cpp
- Unity 2021.3+ LTS (for avatar interface)

---

## Step 1: Setup Backend (5 minutes)

### Install Dependencies

```bash
# Clone if you haven't already
git clone https://github.com/Archamsworth/Lucy.git
cd Lucy/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Backend is pre-configured for localhost. No changes needed for testing!

---

## Step 2: Setup LLM Server (5 minutes)

### Build llama.cpp

```bash
# In a new terminal
cd /path/to/your/projects
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build (choose one):

# Option A: CPU only
make server

# Option B: With CUDA GPU support
mkdir build && cd build
cmake .. -DLLAMA_CUBLAS=ON
cmake --build . --config Release
cd ..
```

### Start LLM Server

```bash
# Place your model in llama.cpp directory
cp /path/to/qwen2.5-3b-instruct.gguf .

# Start server
./build/bin/server -m qwen2.5-3b-instruct.gguf \
  -c 4096 \
  -ngl 20 \
  --port 8001

# Or use the convenience script:
cd /path/to/Lucy
./scripts/start_llm.sh
```

**Keep this terminal open!** You should see:
```
llama server listening at http://0.0.0.0:8001
```

---

## Step 3: Start Backend (2 minutes)

### In a new terminal:

```bash
cd /path/to/Lucy/backend
source venv/bin/activate
python main.py
```

**Keep this terminal open!** You should see:
```
✓ Whisper STT initialized (small)
✓ TTS initialized (piper)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 4: Test Backend (3 minutes)

### Health Check

```bash
# In a new terminal
curl http://localhost:8000/health
```

Expected output:
```json
{
  "api": "online",
  "llm": "online",
  "stt": "available",
  "tts": "available"
}
```

### First Conversation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "message": "Hello Lucy! How are you?"
  }'
```

Expected output (similar to):
```json
{
  "expressions": ["smile", "happy"],
  "text": "Hi there! I'm doing great, thank you for asking!",
  "audio_url": "/audio/tts_xxxxx.wav",
  "raw_response": "*smile*\nHi there! I'm doing great, thank you for asking!\n*happy*"
}
```

✅ **If you see this, the backend is working!**

---

## Step 5: Unity Setup (Optional, 15+ minutes)

This step adds the visual avatar interface. You can skip this and use the API directly if you prefer.

### Quick Setup

1. **Install Unity Hub & Unity 2021.3 LTS**
   - Download: https://unity.com/download

2. **Open Project**
   ```bash
   # In Unity Hub
   # Click "Open" → Navigate to Lucy/Unity/
   ```

3. **Install Dependencies**
   - UniVRM: https://github.com/vrm-c/UniVRM/releases
   - Newtonsoft JSON: `com.unity.nuget.newtonsoft-json`

4. **Import Your Avatar**
   - Drag `.vrm` file into Assets/

5. **Setup Scene**
   - See `Unity/README.md` for detailed scene setup

6. **Test**
   - Click Play
   - Type message
   - See avatar respond!

For detailed Unity setup, see: [Unity/README.md](../Unity/README.md)

---

## Testing Checklist

### Backend Tests
```bash
cd backend/tests

# Unit tests
python test_expression_parser.py      # ✓ Should pass
python test_conversation_manager.py   # ✓ Should pass
python test_input_processor.py        # ✓ Should pass

# Integration tests (requires running servers)
python test_integration.py            # ✓ Should pass
```

### Manual API Tests
```bash
# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a joke", "user_id": "test"}'

# Test conversation memory
curl http://localhost:8000/conversation/test

# Clear conversation
curl -X DELETE http://localhost:8000/conversation/test
```

---

## Common Issues

### "Connection refused" when testing
**Problem:** LLM server or backend not running

**Solution:**
```bash
# Check if servers are running
curl http://localhost:8001/health  # LLM server
curl http://localhost:8000/health  # Backend

# Restart if needed
```

### "Model not found"
**Problem:** Qwen model not in correct location

**Solution:**
```bash
# Copy model to llama.cpp directory
cp /path/to/qwen2.5-3b-instruct.gguf /path/to/llama.cpp/

# Or set environment variable
export MODEL_PATH=/path/to/qwen2.5-3b-instruct.gguf
```

### "ModuleNotFoundError"
**Problem:** Python dependencies not installed

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Out of memory" with LLM
**Problem:** GPU memory insufficient

**Solution:**
```bash
# Use CPU only (set -ngl 0)
./server -m model.gguf -ngl 0 -c 4096 --port 8001

# Or reduce context size
./server -m model.gguf -ngl 20 -c 2048 --port 8001
```

---

## What's Next?

### 1. Explore Features
- Try different message types
- Test expression variety
- Experiment with temperature settings

### 2. Customize
- Edit system prompt in `backend/config.py`
- Adjust expression duration in Unity
- Add custom expressions

### 3. Advanced Setup
- Add speech input (Whisper)
- Enable TTS for audio responses
- Create custom Unity scenes

### 4. Read Documentation
- [SETUP.md](SETUP.md) - Detailed setup
- [API.md](API.md) - API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TESTING.md](TESTING.md) - Testing guide

---

## Quick Command Reference

### Start Services
```bash
# Terminal 1: LLM Server
cd /path/to/llama.cpp
./server -m qwen2.5-3b-instruct.gguf -c 4096 -ngl 20 --port 8001

# Terminal 2: Backend
cd /path/to/Lucy/backend
source venv/bin/activate
python main.py
```

### Test APIs
```bash
# Health check
curl http://localhost:8000/health

# Send message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "test"}'

# Get conversation
curl http://localhost:8000/conversation/test

# Clear conversation
curl -X DELETE http://localhost:8000/conversation/test
```

### Stop Services
```bash
# Press Ctrl+C in each terminal
# Or:
pkill -f "llama.*server"
pkill -f "python main.py"
```

---

## Architecture at a Glance

```
┌─────────────┐
│   Unity     │ ← Visual avatar interface (optional)
│ (Frontend)  │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│   FastAPI   │ ← Main backend server
│  Backend    │
└──────┬──────┘
       │
    ┌──┴──┐
    │     │
┌───▼───┐ │
│ STT   │ │  Whisper speech-to-text (optional)
└───────┘ │
    ┌─────▼─────┐
    │   LLM     │  Qwen2.5-3B via llama.cpp
    │ (Qwen)    │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │   TTS     │  Text-to-speech (optional)
    └───────────┘
```

---

## Support & Resources

**Documentation:**
- 📖 [Full Setup Guide](SETUP.md)
- 📡 [API Documentation](API.md)
- 🏗️ [Architecture](ARCHITECTURE.md)
- 🧪 [Testing Guide](TESTING.md)
- 🎮 [Unity Guide](../Unity/README.md)

**Quick Links:**
- Qwen2.5: https://github.com/QwenLM/Qwen2.5
- llama.cpp: https://github.com/ggerganov/llama.cpp
- UniVRM: https://github.com/vrm-c/UniVRM
- FastAPI: https://fastapi.tiangolo.com/

**Issues?**
- Check the troubleshooting sections
- Review logs in terminal
- Test each component independently

---

## Success! 🎉

If you can:
- ✅ Send messages to the API
- ✅ Get responses with expressions
- ✅ See conversation history

**You're all set!** Lucy is working and ready to use.

Have fun building your virtual companion! 🎭
