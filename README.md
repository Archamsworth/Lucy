# 🎭 Lucy - AI Virtual Companion

A real-time AI virtual companion with emotion-aware responses, natural speech, and expressive VRM avatar animations.

## ✨ Features

- 🧠 **Local LLM**: Qwen2.5-3B-Instruct via llama.cpp
- 🎤 **Speech-to-Text**: faster-whisper (optimized)
- 🔊 **Text-to-Speech**: OpenVoice / Piper TTS
- 👤 **VRM Avatar**: Full expression and animation support
- 💬 **Conversational Memory**: Context-aware responses
- 😊 **Expression System**: Emotion-driven facial animations
- ⚡ **Real-Time**: Low latency, optimized for performance

## 🏗️ Architecture

```
Unity (UI + VRM Avatar)
        ↓
Python FastAPI Backend
        ↓
Whisper (if speech)
        ↓
Qwen2.5-3B
        ↓
Expression Parser
        ↓
TTS
        ↓
Unity (Audio + Animation Sync)
```

## 📋 Prerequisites

### Backend
- Python 3.10+
- llama.cpp server
- Qwen2.5-3B-Instruct GGUF model ✅
- (Optional) faster-whisper
- (Optional) OpenVoice or Piper TTS

### Unity
- Unity 2021.3+ LTS
- UniVRM package
- VRM avatar model ✅
- Newtonsoft JSON (com.unity.nuget.newtonsoft-json)

## 🚀 Quick Start

### 1. Start llama.cpp Server

```bash
cd /path/to/llama.cpp
./server -m qwen2.5-3b-instruct.gguf \
  -c 4096 \
  -ngl 20 \
  --host 0.0.0.0 \
  --port 8001
```

### 2. Start Backend API

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API will be available at `http://localhost:8000`

### 3. Setup Unity Project

1. Create new Unity project (2021.3 LTS or newer)
2. Install UniVRM package:
   - Download from: https://github.com/vrm-c/UniVRM/releases
   - Import `.unitypackage`
3. Import Newtonsoft JSON:
   - Window → Package Manager → Add package from git URL
   - `com.unity.nuget.newtonsoft-json`
4. Import your VRM avatar model
5. Copy Unity scripts to `Assets/Scripts/`
6. Attach scripts to avatar GameObject:
   - `LucyController.cs` - Main controller
   - `ExpressionController.cs` - Facial expressions
   - `IdleAnimationController.cs` - Idle animations

### 4. Configure Unity Scene

1. Drag VRM avatar into scene
2. Add `LucyController` component
3. Add `ExpressionController` component
4. Add `IdleAnimationController` component
5. Assign references:
   - Animator
   - AudioSource
   - Chest Bone
   - Head Bone
6. Set API URL in LucyController: `http://localhost:8000`

## 🎮 Usage

### Text Chat

```csharp
// From any script
LucyController lucy = FindObjectOfType<LucyController>();
lucy.SendMessage("Hello Lucy!");
```

### Clear Conversation

```csharp
lucy.ClearConversation();
```

## 🎨 Expression System

### Available Expressions

- `*smile*` - Joy/Happy
- `*smirk*` - Confident
- `*giggle*` - Playful laugh
- `*pout*` - Sad/Disappointed
- `*blush*` / `*shy*` - Shy/Embarrassed
- `*angry*` - Angry/Annoyed
- `*excited*` - Surprised/Excited

### System Prompt

The AI is trained to use expression tags in responses:

```
*smile*
I'm so glad to see you!
*giggle*
You're really funny!
```

These are automatically:
1. Parsed from response
2. Removed from TTS text
3. Triggered as VRM blendshape animations

## 🔧 Configuration

### Backend Settings

Edit `backend/main.py`:

```python
LLAMA_CPP_URL = "http://localhost:8001/v1/chat/completions"
MAX_HISTORY = 6  # Conversation memory length
```

### LLM Parameters

```python
{
    "temperature": 0.8,      # Creativity (0.0-1.0)
    "top_p": 0.9,            # Nucleus sampling
    "max_tokens": 200,       # Response length
    "repeat_penalty": 1.1    # Reduce repetition
}
```

### Unity Settings

In `LucyController`:
- `apiBaseUrl`: Backend API endpoint
- `expressionDuration`: How long each expression lasts
- `transitionSpeed`: Expression blend speed

## 📡 API Endpoints

### POST `/chat`
Send text message to Lucy

**Request:**
```json
{
  "user_id": "default",
  "message": "Hello!",
  "temperature": 0.8,
  "max_tokens": 200
}
```

**Response:**
```json
{
  "expressions": ["smile", "giggle"],
  "text": "Hi there! I'm so happy to see you!",
  "audio_path": null,
  "raw_response": "*smile*\nHi there! I'm so happy to see you!\n*giggle*"
}
```

### GET `/health`
Check service status

### DELETE `/conversation/{user_id}`
Clear conversation history

### GET `/conversation/{user_id}`
Get conversation history

## 🎯 Optimization Tips

### Performance
- Use `int8` quantization for Whisper
- Keep `max_tokens` ≤ 200 for faster responses
- Limit conversation history to 6 exchanges
- Use `ngl` parameter in llama.cpp for GPU offload

### Quality
- Adjust `temperature` (0.7-0.9) for personality
- Use VRM with good blendshape support
- Add custom expressions to `ExpressionController.cs`

## 🔮 Future Enhancements

- [ ] OpenVoice TTS integration
- [ ] Real-time voice input
- [ ] Lip-sync (SALSA/OVR)
- [ ] Custom personality profiles
- [ ] Multi-language support
- [ ] Gesture animations
- [ ] RAG for long-term memory

## 🐛 Troubleshooting

### "LLM service error"
- Ensure llama.cpp server is running on port 8001
- Check model path is correct
- Verify `ngl` value matches your GPU

### "No animator assigned"
- Make sure VRM model has Animator component
- Attach animator reference in LucyController

### Expression not working
- Check VRM model has blendshapes
- Verify BlendShapeProxy component exists
- Match expression names in Animator Controller

## 📄 License

MIT License - feel free to modify and use!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 💖 Credits

- **LLM**: Qwen2.5 by Alibaba
- **Runtime**: llama.cpp
- **VRM**: UniVRM by VRM Consortium
- **STT**: faster-whisper
- **TTS**: OpenVoice / Piper

---

Built with ❤️ for the AI companion community
