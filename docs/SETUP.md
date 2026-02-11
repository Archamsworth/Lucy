# Lucy Virtual Companion - Setup Guide

Complete setup instructions for the Lucy AI Virtual Companion system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [LLM Server Setup](#llm-server-setup)
4. [Unity Setup](#unity-setup)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS:** Linux, macOS, or Windows 10/11
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 10GB free space
- **GPU:** Optional but recommended for better performance

### Software Requirements

#### Backend
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool (venv or conda)

#### LLM
- llama.cpp (will be built from source)
- C/C++ compiler (gcc, clang, or MSVC)
- cmake (for building llama.cpp)
- Git

#### Unity
- Unity 2021.3 LTS or newer
- Visual Studio or VS Code with C# extension

#### Models (Required)
- ✅ Qwen2.5-3B-Instruct GGUF model (you already have this)
- ✅ VRM avatar model (you already have this)

---

## Backend Setup

### 1. Clone Repository
```bash
cd /path/to/your/projects
git clone https://github.com/Archamsworth/Lucy.git
cd Lucy
```

### 2. Create Python Virtual Environment
```bash
cd backend

# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using conda
conda create -n lucy python=3.10
conda activate lucy
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Core dependencies installed:**
- fastapi - Web framework
- uvicorn - ASGI server
- faster-whisper - Speech-to-text
- requests - HTTP client
- pydantic - Data validation
- python-multipart - File upload support

### 4. Install Optional Dependencies

#### For TTS (Text-to-Speech)
```bash
# Option 1: Piper TTS (lightweight, recommended)
pip install piper-tts

# Option 2: Coqui TTS (more features)
pip install TTS

# Option 3: OpenVoice (highest quality)
# Follow: https://github.com/myshell-ai/OpenVoice
```

### 5. Verify Installation
```bash
python -c "import fastapi; import faster_whisper; print('Backend dependencies OK')"
```

---

## LLM Server Setup

### 1. Install llama.cpp

```bash
cd /path/to/your/projects

# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with GPU support (CUDA)
mkdir build && cd build
cmake .. -DLLAMA_CUBLAS=ON
cmake --build . --config Release

# OR build without GPU (CPU only)
make server

# The server binary will be at: ./build/bin/server
```

### 2. Place Model File

```bash
# Copy your Qwen model to llama.cpp directory
cp /path/to/qwen2.5-3b-instruct.gguf /path/to/llama.cpp/

# OR set MODEL_PATH environment variable
export MODEL_PATH=/path/to/qwen2.5-3b-instruct.gguf
```

### 3. Test LLM Server

```bash
cd /path/to/llama.cpp

# Start server (adjust -ngl for GPU layers)
./build/bin/server -m qwen2.5-3b-instruct.gguf \
  -c 4096 \
  -ngl 20 \
  --host 0.0.0.0 \
  --port 8001

# Test in another terminal
curl http://localhost:8001/health
```

**Server Parameters:**
- `-m` - Model path
- `-c` - Context window size (4096 for Qwen2.5)
- `-ngl` - Number of GPU layers (0 = CPU only, 20-33 for 3B model)
- `--port` - Server port (default: 8001)

### 4. Use Convenience Script

```bash
cd /path/to/Lucy

# Edit scripts/start_llm.sh with your paths
nano scripts/start_llm.sh

# Make executable
chmod +x scripts/start_llm.sh

# Run
./scripts/start_llm.sh
```

---

## Unity Setup

### 1. Install Unity Hub

Download from: https://unity.com/download

### 2. Install Unity Editor

- Open Unity Hub
- Go to "Installs"
- Click "Install Editor"
- Select **Unity 2021.3 LTS** or newer
- Include modules:
  - Windows Build Support (if on Linux/Mac)
  - Linux Build Support (if on Windows/Mac)
  - Visual Studio Community (or your preferred IDE)

### 3. Create/Open Unity Project

#### Option A: Create New Project
```bash
# Open Unity Hub
# Click "New Project"
# Select "3D" template
# Name: "LucyCompanion"
# Create project
```

#### Option B: Import Existing
```bash
# Open Unity Hub
# Click "Open"
# Navigate to: Lucy/Unity/
# Open project
```

### 4. Install UniVRM Package

```bash
# Download UniVRM from:
# https://github.com/vrm-c/UniVRM/releases

# In Unity:
# Assets → Import Package → Custom Package
# Select downloaded UniVRM .unitypackage
# Import all
```

### 5. Install Newtonsoft JSON

```bash
# In Unity:
# Window → Package Manager
# Click "+" → Add package from git URL
# Enter: com.unity.nuget.newtonsoft-json
# Click "Add"
```

### 6. Import Scripts

```bash
# Copy scripts from repository
cp -r Lucy/Unity/Assets/Scripts /path/to/Unity/Project/Assets/

# Or in Unity:
# Assets → Import New Asset
# Navigate to Lucy/Unity/Assets/Scripts
# Import all
```

### 7. Import VRM Avatar

```bash
# In Unity:
# Assets → Import New Asset
# Select your .vrm file
# Wait for import to complete

# Drag VRM into scene
# The avatar will be automatically configured
```

---

## Configuration

### Backend Configuration

Edit `backend/config.py`:

```python
# LLM Settings
LLAMA_CPP_HOST = "localhost"
LLAMA_CPP_PORT = 8001

# Whisper Settings
WHISPER_MODEL_SIZE = "small"  # tiny, base, small, medium
WHISPER_DEVICE = "cpu"        # cpu or cuda
WHISPER_COMPUTE_TYPE = "int8" # int8, float16, float32

# TTS Settings
TTS_ENGINE = "piper"  # piper, coqui, or openvoice
TTS_VOICE = "en_US-lessac-medium"

# Conversation
MAX_CONVERSATION_HISTORY = 6  # Number of exchanges to remember
```

### Unity Configuration

Create `Unity/Assets/Resources/config.json`:

```json
{
  "backendURL": "http://localhost:8000",
  "micSampleRate": 16000,
  "maxRecordingLength": 30,
  "idleAnimationInterval": 3.0
}
```

### Setup Avatar in Unity

1. **Create Main Scene**
   - File → New Scene
   - Save as "MainScene"

2. **Add Avatar**
   - Drag VRM prefab into Hierarchy
   - Position at (0, 0, 0)

3. **Add Lucy Controller**
   - Create Empty GameObject: "LucyController"
   - Add Component → VirtualCompanionController
   - Add Component → ExpressionController  
   - Add Component → IdleAnimationController

4. **Configure Components**
   - VirtualCompanionController:
     - API Base URL: http://localhost:8000
     - User ID: default
     - Expression Controller: (drag ExpressionController)
     - Audio Source: (auto-created)
   
   - ExpressionController:
     - Blend Shape Proxy: (drag from VRM avatar)
     - Animator: (drag from VRM avatar)
   
   - IdleAnimationController:
     - Chest Bone: (find in VRM skeleton)
     - Head Bone: (find in VRM skeleton)

5. **Add UI Canvas**
   - GameObject → UI → Canvas
   - Add → UI → InputField (for text input)
   - Add → UI → Button (for send button)
   - Add → UI → Button (for mic button)
   - Add → UI → Text (for chat history)

6. **Add UI Manager**
   - Add UIManager script to Canvas
   - Assign all UI elements in inspector
   - Assign VirtualCompanionController reference

---

## Testing

### Test Backend

```bash
# Terminal 1: Start LLM server
cd /path/to/llama.cpp
./scripts/start_llm.sh

# Terminal 2: Start backend
cd /path/to/Lucy/backend
source venv/bin/activate
python main.py

# Terminal 3: Test endpoints
curl http://localhost:8000/health

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "test"}'
```

### Test Unity

1. **Play Mode Test**
   - Click Play button in Unity
   - Type message in input field
   - Click Send
   - Observe avatar response

2. **Speech Test**
   - Click microphone button
   - Speak clearly
   - Click stop
   - Wait for response

3. **Expression Test**
   - Send: "Tell me a joke" (should trigger *smile* or *giggle*)
   - Send: "I'm sad" (should trigger *pout* or sympathetic expression)

### Run Unit Tests

```bash
cd /path/to/Lucy/backend/tests
python test_expression_parser.py
python test_conversation_manager.py
python test_input_processor.py
```

---

## Troubleshooting

### Backend Issues

**Problem: "LLM service error: Connection refused"**
- Solution: Ensure llama.cpp server is running on port 8001
- Check: `curl http://localhost:8001/health`

**Problem: "ModuleNotFoundError: No module named 'faster_whisper'"**
- Solution: Activate venv and reinstall: `pip install -r requirements.txt`

**Problem: "No speech detected in audio"**
- Solution: Check microphone permissions
- Try: Record longer audio (3+ seconds)
- Verify: Audio file is not empty

### LLM Server Issues

**Problem: "Model not found"**
- Solution: Check model path is correct
- Verify: File exists and has .gguf extension

**Problem: "Out of memory"**
- Solution: Reduce `-ngl` parameter (use less GPU)
- Try: `-ngl 0` for CPU-only mode
- Reduce: Context size with `-c 2048`

### Unity Issues

**Problem: "VRMBlendShapeProxy not found"**
- Solution: Ensure VRM model is properly imported
- Check: Avatar has VRMBlendShapeProxy component

**Problem: "No animator assigned"**
- Solution: Assign Animator from VRM avatar to ExpressionController

**Problem: "Microphone not detected"**
- Solution: Grant microphone permissions to Unity
- Check: System settings → Privacy → Microphone

**Problem: "JSON serialization error"**
- Solution: Verify Newtonsoft.Json is installed
- Check: Package Manager shows package installed

### Network Issues

**Problem: "CORS error in browser/Unity"**
- Solution: Already configured in backend (allow_origins=["*"])
- Verify: Backend is running and accessible

**Problem: "Connection timeout"**
- Solution: Check firewall settings
- Try: Disable antivirus temporarily
- Verify: Backend URL is correct in Unity

---

## Performance Optimization

### Backend
```python
# config.py
WHISPER_MODEL_SIZE = "base"  # Use smaller model for speed
WHISPER_COMPUTE_TYPE = "int8"  # Faster inference
DEFAULT_MAX_TOKENS = 150  # Shorter responses
```

### LLM Server
```bash
# Use more GPU layers for speed
-ngl 33  # Full offload for 3B model

# Reduce context if not needed
-c 2048

# Increase threads
--threads 8
```

### Unity
- Use VRM with fewer polygons (< 50K)
- Optimize blend shapes (< 50 shapes)
- Reduce texture sizes
- Disable unnecessary features

---

## Next Steps

1. ✅ Verify all services are running
2. ✅ Test basic chat functionality
3. ✅ Test speech input (if available)
4. ✅ Test expressions and animations
5. ✅ Customize system prompt for your use case
6. ✅ Add custom expressions/animations
7. ✅ Deploy for production (optional)

## Additional Resources

- **UniVRM Docs:** https://vrm.dev/en/univrm/
- **llama.cpp:** https://github.com/ggerganov/llama.cpp
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Faster Whisper:** https://github.com/guillaumekln/faster-whisper

---

**Need Help?** 
- Check logs in `backend/` directory
- Review error messages carefully
- Test each component independently
- Ask in GitHub Issues
