# Lucy Virtual Companion - Testing Checklist

## Prerequisites
- [ ] Python 3.10+ installed
- [ ] Unity 2021.3+ LTS installed
- [ ] llama.cpp built successfully
- [ ] Qwen2.5-3B model file available
- [ ] VRM avatar model available

---

## Backend Unit Tests

### Expression Parser Tests
```bash
cd backend/tests
python test_expression_parser.py
```

**Expected Results:**
- [ ] All 12 tests pass
- [ ] Single expression parsing works
- [ ] Multiple expressions parsing works
- [ ] Invalid expressions filtered correctly
- [ ] Whitespace normalized properly

### Conversation Manager Tests
```bash
python test_conversation_manager.py
```

**Expected Results:**
- [ ] All 10 tests pass
- [ ] History trimming works correctly
- [ ] Multiple users isolated
- [ ] Metadata tracking works

### Input Processor Tests
```bash
python test_input_processor.py
```

**Expected Results:**
- [ ] All 12 tests pass
- [ ] Text validation works
- [ ] Audio validation works
- [ ] Error handling correct

---

## Backend Integration Tests

### 1. Health Check
```bash
# Start LLM server first
cd /path/to/llama.cpp
./server -m qwen2.5-3b-instruct.gguf -c 4096 -ngl 20 --port 8001

# Start backend (in new terminal)
cd /path/to/Lucy/backend
source venv/bin/activate
python main.py

# Test health (in new terminal)
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "api": "online",
  "llm": "online",
  "stt": "available",
  "tts": "available"
}
```

**Checklist:**
- [ ] Health endpoint responds
- [ ] API status is "online"
- [ ] LLM status is "online"
- [ ] No errors in backend console

### 2. Text Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "message": "Hello Lucy!",
    "temperature": 0.8,
    "max_tokens": 200
  }'
```

**Expected Response:**
```json
{
  "expressions": ["smile", "happy"],
  "text": "Hi there! I'm so glad to see you!",
  "audio_url": "/audio/tts_xxxxx.wav",
  "raw_response": "*smile*\nHi there! I'm so glad to see you!\n*happy*"
}
```

**Checklist:**
- [ ] Response received within 5 seconds
- [ ] Expressions array populated
- [ ] Clean text without expression tags
- [ ] Audio URL returned (if TTS enabled)
- [ ] Raw response contains expression tags

### 3. Expression Extraction
```bash
# Test various emotions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Tell me a joke"}'
```

**Expected:**
- [ ] Response contains expressions like smile, giggle, laugh
- [ ] Expression tags removed from text
- [ ] Multiple expressions handled correctly

### 4. Conversation Memory
```bash
# Send first message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "memory_test", "message": "My name is Alice"}'

# Send follow-up
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "memory_test", "message": "What is my name?"}'

# Check history
curl http://localhost:8000/conversation/memory_test
```

**Expected:**
- [ ] Second response mentions "Alice"
- [ ] History shows both exchanges
- [ ] Message count is correct

### 5. Clear Conversation
```bash
curl -X DELETE http://localhost:8000/conversation/test
```

**Expected:**
- [ ] Success message returned
- [ ] History cleared when checked

### 6. Speech Endpoint (if Whisper installed)
```bash
# Record audio file first (use Audacity, etc.)
# Then:
curl -X POST http://localhost:8000/speech \
  -F "audio=@test_audio.wav" \
  -F "user_id=test"
```

**Expected:**
- [ ] Audio transcribed correctly
- [ ] Response generated based on transcription
- [ ] Same response format as /chat endpoint

---

## Backend Error Handling

### 1. Empty Message
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": ""}'
```

**Expected:**
- [ ] HTTP 400 error
- [ ] Error message about empty input

### 2. LLM Offline
```bash
# Stop LLM server
# Then:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hello"}'
```

**Expected:**
- [ ] HTTP 503 error
- [ ] Error message about LLM service

### 3. Invalid Audio File
```bash
curl -X POST http://localhost:8000/speech \
  -F "audio=@invalid.txt"
```

**Expected:**
- [ ] HTTP 400 error
- [ ] Error about invalid audio

---

## Unity Tests

### 1. Scene Setup
**Manual Steps:**
1. Open Unity project
2. Open MainScene
3. Check hierarchy has:
   - [ ] VRM Avatar
   - [ ] LucyController (with components)
   - [ ] Canvas (with UI elements)
   - [ ] EventSystem

### 2. Component Configuration
**Check Inspector:**
- [ ] VirtualCompanionController has API URL set
- [ ] ExpressionController has VRMBlendShapeProxy assigned
- [ ] IdleAnimationController has Chest and Head bones assigned
- [ ] UIManager has all UI elements assigned

### 3. Play Mode - Text Chat
**Manual Steps:**
1. Click Play in Unity
2. Type "Hello Lucy!" in input field
3. Click Send button

**Expected:**
- [ ] Message clears from input field
- [ ] Status shows "Processing..."
- [ ] Avatar expression changes
- [ ] Status shows "Lucy is speaking..."
- [ ] Audio plays (if TTS enabled)
- [ ] Avatar returns to idle
- [ ] Response appears in chat history

### 4. Play Mode - Expression Variety
**Test Messages:**

```
Message: "I'm so happy today!"
Expected: smile, happy expressions
[ ] Expression displayed correctly

Message: "I'm feeling sad"
Expected: pout, sad expressions
[ ] Expression displayed correctly

Message: "That's hilarious!"
Expected: laugh, giggle expressions
[ ] Expression displayed correctly

Message: "I'm angry!"
Expected: angry expression
[ ] Expression displayed correctly
```

### 5. Play Mode - Idle Animations
**Observe for 30 seconds:**
- [ ] Avatar blinks periodically (every 3-5 seconds)
- [ ] Subtle breathing motion visible
- [ ] Head moves slightly/naturally
- [ ] No jerky or unnatural movements

### 6. Play Mode - Speech Input (if microphone available)
**Manual Steps:**
1. Click microphone button
2. Speak: "Hello Lucy, how are you?"
3. Click stop button

**Expected:**
- [ ] Button changes to "Stop" while recording
- [ ] Status shows "Listening..."
- [ ] Recording stops on button click
- [ ] Status shows "Processing..."
- [ ] Response received and displayed
- [ ] Same behavior as text input

### 7. Play Mode - Clear Conversation
**Manual Steps:**
1. Send several messages
2. Click Clear button

**Expected:**
- [ ] Chat history clears
- [ ] Status confirms cleared
- [ ] Next message starts fresh conversation

### 8. Play Mode - Error Handling
**Test without backend running:**
1. Stop backend server
2. Try sending message in Unity

**Expected:**
- [ ] Error message displayed
- [ ] UI remains responsive
- [ ] Can retry after backend starts

---

## Performance Tests

### 1. Response Time - Text
**Test 10 messages:**
```bash
for i in {1..10}; do
  time curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"user_id": "perf_test", "message": "Test message '$i'"}'
  echo ""
done
```

**Expected:**
- [ ] Average response time < 3 seconds
- [ ] No timeouts
- [ ] Consistent performance

### 2. Memory Usage
**Monitor during operation:**
- [ ] Backend RAM usage stable (< 2GB)
- [ ] LLM server RAM usage acceptable
- [ ] No memory leaks over time

### 3. Concurrent Users
```bash
# Run multiple curl requests simultaneously
for i in {1..5}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"user_id": "user'$i'", "message": "Hello"}' &
done
wait
```

**Expected:**
- [ ] All requests handled successfully
- [ ] No race conditions
- [ ] Users isolated correctly

---

## Audio Tests (if TTS enabled)

### 1. Audio Generation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "audio_test", "message": "Hello"}'

# Check audio file exists
curl http://localhost:8000/audio/tts_xxxxx.wav --output test.wav
```

**Expected:**
- [ ] Audio URL returned in response
- [ ] Audio file downloadable
- [ ] Audio plays correctly
- [ ] Audio matches text content

### 2. Expression-Aware TTS
**Test different emotions:**
- [ ] Happy expressions have warm tone
- [ ] Sad expressions have gentle tone
- [ ] Angry expressions have firm tone

---

## Edge Cases

### 1. Very Long Message
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "'$(python -c "print('a' * 1001)")'"}'
```

**Expected:**
- [ ] HTTP 400 error
- [ ] Error about message length

### 2. Special Characters
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hello 🎭 *test* <script>"}'
```

**Expected:**
- [ ] Handled gracefully
- [ ] No code injection
- [ ] Response appropriate

### 3. Rapid Fire Messages
```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"user_id": "rapid", "message": "Message '$i'"}'
done
```

**Expected:**
- [ ] All messages handled
- [ ] History maintained correctly
- [ ] No errors

---

## Final Verification

### Backend Checklist
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Error handling works
- [ ] Performance acceptable
- [ ] No memory leaks
- [ ] Logs are clean

### Unity Checklist
- [ ] Scene configured correctly
- [ ] Components working
- [ ] UI responsive
- [ ] Expressions display
- [ ] Idle animations work
- [ ] Audio plays
- [ ] Error messages clear

### Overall System
- [ ] End-to-end flow works
- [ ] User experience smooth
- [ ] No critical bugs
- [ ] Documentation accurate
- [ ] Ready for use

---

## Known Issues / Limitations

Document any issues found:

1. Issue: _______________
   Impact: _______________
   Workaround: _______________

2. Issue: _______________
   Impact: _______________
   Workaround: _______________

---

## Testing Notes

Date Tested: _______________
Tester: _______________
Environment: _______________
Results: _______________
