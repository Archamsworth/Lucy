# Lucy Virtual Companion - Architecture

## System Overview

Lucy is a real-time AI virtual companion system that combines:
- **Language Model** (Qwen2.5-3B) for natural conversation
- **Speech Recognition** (Whisper) for voice input
- **Text-to-Speech** for audio responses
- **3D Avatar** (VRM) with emotion-driven animations
- **Expression System** for emotional awareness

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Unity Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  UI Layer    │  │ Avatar Layer │  │  Audio Layer      │  │
│  │              │  │              │  │                   │  │
│  │ - InputField │  │ - VRM Model  │  │ - Microphone     │  │
│  │ - Buttons    │  │ - Expressions│  │ - Audio Player   │  │
│  │ - Chat Log   │  │ - Animations │  │ - TTS Playback   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │ Network Layer   │                        │
│                   │  (HTTP Client)  │                        │
│                   └────────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │
                        HTTP/REST
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend                           │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────┐ │
│  │   Endpoints  │  │   Middleware  │  │    Components     │ │
│  │              │  │               │  │                   │ │
│  │ /chat        │  │ - CORS        │  │ - Input Processor│ │
│  │ /speech      │  │ - Static Files│  │ - LLM Client     │ │
│  │ /conversation│  │ - Logging     │  │ - Expression     │ │
│  │ /health      │  │               │  │   Parser         │ │
│  │              │  │               │  │ - Conversation   │ │
│  │              │  │               │  │   Manager        │ │
│  │              │  │               │  │ - TTS Handler    │ │
│  └──────┬───────┘  └───────────────┘  └────────┬──────────┘ │
│         │                                       │            │
└─────────┼───────────────────────────────────────┼────────────┘
          │                                       │
          │                                       │
    ┌─────▼─────┐                          ┌─────▼──────┐
    │  Whisper  │                          │    TTS     │
    │    STT    │                          │  Engine    │
    └───────────┘                          └────────────┘
          │
          │
    ┌─────▼──────────────────────────────────────┐
    │         llama.cpp Server                   │
    │                                            │
    │  ┌──────────────────────────────────────┐ │
    │  │   Qwen2.5-3B-Instruct (GGUF)        │ │
    │  │   - Context: 4096 tokens            │ │
    │  │   - Quantization: Q4/Q8             │ │
    │  │   - GPU Layers: 0-33                │ │
    │  └──────────────────────────────────────┘ │
    └────────────────────────────────────────────┘
```

## Data Flow

### Text Message Flow
```
1. User types message in Unity UI
   ↓
2. Unity sends HTTP POST to /chat
   ↓
3. Backend processes input (validation, cleaning)
   ↓
4. Conversation history retrieved
   ↓
5. Messages sent to llama.cpp (LLM inference)
   ↓
6. Response parsed for expressions
   ↓
7. TTS synthesizes audio (optional)
   ↓
8. Response returned to Unity
   ↓
9. Unity triggers expressions on avatar
   ↓
10. Unity plays TTS audio
   ↓
11. Avatar returns to idle state
```

### Speech Message Flow
```
1. User clicks mic button in Unity
   ↓
2. Unity records audio from microphone
   ↓
3. User clicks stop
   ↓
4. Unity converts AudioClip to WAV
   ↓
5. Unity sends HTTP POST to /speech with audio file
   ↓
6. Backend validates audio file
   ↓
7. Whisper transcribes audio to text
   ↓
8. [Same as steps 3-11 from text flow]
```

## Component Details

### Backend Components

#### 1. FastAPI Server (`main.py`)
- **Role:** HTTP server and request router
- **Responsibilities:**
  - Handle HTTP requests
  - Route to appropriate handlers
  - Manage CORS
  - Serve static audio files
  - Error handling and logging

#### 2. LLM Client (`llm_client.py`)
- **Role:** Interface to llama.cpp server
- **Responsibilities:**
  - Send messages to LLM
  - Handle timeouts and retries
  - Configure inference parameters
  - Health check LLM service

#### 3. Expression Parser (`expression_parser.py`)
- **Role:** Extract emotion tags from text
- **Responsibilities:**
  - Find all `*expression*` tags
  - Validate expressions
  - Remove tags from text
  - Return clean text and expressions list

#### 4. Conversation Manager (`conversation_manager.py`)
- **Role:** Maintain conversation context
- **Responsibilities:**
  - Store message history per user
  - Trim to maximum history length
  - Format messages for LLM
  - Track metadata (timestamps, counts)

#### 5. Input Processor (`input_processor.py`)
- **Role:** Validate and process inputs
- **Responsibilities:**
  - Clean text input
  - Validate audio files
  - Interface with STT engine
  - Error handling for invalid inputs

#### 6. TTS Handler (`tts_handler.py`)
- **Role:** Synthesize speech from text
- **Responsibilities:**
  - Interface with TTS engine
  - Cache generated audio
  - Clean up old audio files
  - Handle expression-aware synthesis

### Unity Components

#### 1. VirtualCompanionController
- **Role:** Main orchestrator
- **Responsibilities:**
  - Coordinate all systems
  - Manage state machine
  - Send/receive messages
  - Handle responses

#### 2. ExpressionController
- **Role:** Facial expression management
- **Responsibilities:**
  - Control VRM blend shapes
  - Queue expressions
  - Smooth transitions
  - Reset to neutral

#### 3. IdleAnimationController
- **Role:** Idle behavior
- **Responsibilities:**
  - Automatic blinking
  - Breathing animation
  - Head movements
  - Natural idle state

#### 4. UIManager
- **Role:** User interface
- **Responsibilities:**
  - Handle user input
  - Display conversation
  - Show status messages
  - Control buttons

#### 5. MicrophoneRecorder
- **Role:** Audio recording
- **Responsibilities:**
  - Record from microphone
  - Convert to WAV format
  - Trim recordings
  - Handle permissions

## State Machine

### Companion States

```
    ┌────────┐
    │  Idle  │ ◄─────────┐
    └───┬────┘           │
        │                │
        │ User speaks    │
        │                │
    ┌───▼───────┐        │
    │ Listening │        │
    └───┬───────┘        │
        │                │
        │ Audio sent     │
        │                │
    ┌───▼───────┐        │
    │Processing │        │
    └───┬───────┘        │
        │                │
        │ Response ready │
        │                │
    ┌───▼────────┐       │
    │  Speaking  ├───────┘
    └────────────┘
```

**State Descriptions:**

- **Idle:** Ready for input, idle animations active
- **Listening:** Recording audio from microphone
- **Processing:** Sending to backend, waiting for response
- **Speaking:** Playing audio, displaying expressions

## Expression System

### Expression Tags → Blend Shapes

```python
Expression Mapping:
{
    "smile"     → VRM BlendShapePreset.Joy
    "giggle"    → VRM BlendShapePreset.Joy
    "laugh"     → VRM BlendShapePreset.Joy
    "happy"     → VRM BlendShapePreset.Joy
    "excited"   → VRM BlendShapePreset.Joy
    
    "smirk"     → VRM BlendShapePreset.Fun
    
    "pout"      → VRM BlendShapePreset.Sorrow
    "sad"       → VRM BlendShapePreset.Sorrow
    "shy"       → VRM BlendShapePreset.Sorrow
    "worried"   → VRM BlendShapePreset.Sorrow
    
    "angry"     → VRM BlendShapePreset.Angry
    
    "surprised" → VRM BlendShapePreset.Surprised
    "confused"  → VRM BlendShapePreset.Surprised
    
    "thinking"  → VRM BlendShapePreset.Neutral
}
```

### Expression Lifecycle

```
1. LLM generates: "*smile*\nHello there!\n*giggle*"
   ↓
2. Parser extracts: ["smile", "giggle"]
   ↓
3. Parser cleans: "Hello there!"
   ↓
4. Unity receives both
   ↓
5. Queue expressions: smile → giggle
   ↓
6. Play "smile" for 2 seconds
   ↓
7. Fade out, play "giggle" for 2 seconds
   ↓
8. Fade out, return to neutral
```

## Conversation Management

### Message History Structure

```json
{
  "user_id": "default",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "*smile*\nHi!"},
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "*happy*\nI'm great!"}
  ]
}
```

### History Trimming

```
Maximum: 6 exchanges (12 messages)

When limit reached:
[msg1, msg2, msg3, msg4, ... msg11, msg12] (full)
          ↓
[msg3, msg4, msg5, msg6, ... msg13, msg14] (new added, old removed)
```

### Message Formatting for LLM

```
Final prompt sent to LLM:
[
  {role: "system", content: SYSTEM_PROMPT},
  {role: "user", content: "msg1"},
  {role: "assistant", content: "response1"},
  {role: "user", content: "msg2"},
  {role: "assistant", content: "response2"},
  ...
  {role: "user", content: "new_message"}
]
```

## Performance Considerations

### Latency Targets

| Operation | Target | Acceptable |
|-----------|--------|-----------|
| Text Input → Response | < 2s | < 5s |
| Speech Input → Transcription | < 3s | < 6s |
| LLM Inference | < 2s | < 4s |
| TTS Generation | < 1s | < 3s |
| Total (Text) | < 3s | < 8s |
| Total (Speech) | < 5s | < 12s |

### Optimization Strategies

**Backend:**
- Async operations (FastAPI)
- Request/response caching
- Pre-warm models
- Audio file cleanup
- Connection pooling

**LLM Server:**
- GPU acceleration (CUDA)
- Context caching
- Batch processing
- Optimal quantization (Q4/Q8)

**Unity:**
- Asset bundling
- Texture compression
- LOD for avatars
- Audio streaming
- Coroutine-based async

## Security Considerations

### Current Implementation (Local)
- No authentication required
- All endpoints public
- CORS fully open
- No rate limiting

### Production Recommendations
- Add API key authentication
- Implement rate limiting
- Restrict CORS origins
- Add input sanitization
- Encrypt sensitive data
- Use HTTPS
- Implement user sessions
- Add request logging

## Scalability

### Current Limitations
- Single-threaded LLM server
- In-memory conversation storage
- Local file audio storage
- No load balancing

### Scale-Up Strategies
- Use Redis for conversation storage
- S3/cloud storage for audio files
- Multiple LLM server instances
- Load balancer (nginx)
- Database for analytics
- WebSocket for real-time
- CDN for audio delivery

## Error Handling

### Backend Error Flow
```
1. Request received
   ↓
2. Validation (400 if invalid)
   ↓
3. Process request
   ↓
4. External service call (503 if unavailable)
   ↓
5. Response (500 if internal error)
```

### Unity Error Flow
```
1. Send request
   ↓
2. Network error? → Show error message
   ↓
3. Parse response
   ↓
4. Response error? → Show error message
   ↓
5. Process successfully
```

## Testing Strategy

### Backend Tests
- **Unit Tests:** Individual components
- **Integration Tests:** API endpoints
- **Load Tests:** Performance under load

### Unity Tests
- **Play Mode Tests:** Runtime behavior
- **Edit Mode Tests:** Component validation
- **Manual Tests:** User experience

## Future Enhancements

### Planned Features
1. **WebSocket support** for real-time streaming
2. **Voice cloning** with custom TTS models
3. **Multi-language** support (i18n)
4. **Gesture system** for body animations
5. **RAG integration** for long-term memory
6. **Multiple avatars** with personality profiles
7. **Mobile support** (iOS/Android builds)
8. **VR support** (Quest, PCVR)

### Technical Debt
- [ ] Add comprehensive logging
- [ ] Implement proper caching
- [ ] Add metrics/monitoring
- [ ] Improve error messages
- [ ] Add request tracing
- [ ] Optimize asset loading
- [ ] Add automated tests
- [ ] Document all APIs

---

## References

- **Qwen2.5:** https://github.com/QwenLM/Qwen2.5
- **llama.cpp:** https://github.com/ggerganov/llama.cpp
- **VRM:** https://vrm.dev/
- **FastAPI:** https://fastapi.tianglio.com/
- **Whisper:** https://github.com/openai/whisper
- **Unity:** https://unity.com/

---

Last Updated: 2024-02-11
