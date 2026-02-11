# Lucy API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required for local development.

## Endpoints

### GET `/`
Get API information

**Response:**
```json
{
  "message": "Lucy AI Companion API",
  "status": "online",
  "version": "1.0.0",
  "features": {
    "chat": true,
    "stt": true,
    "tts": true
  }
}
```

---

### GET `/health`
Check service health status

**Response:**
```json
{
  "api": "online",
  "llm": "online",
  "stt": "available",
  "tts": "available"
}
```

**Status Meanings:**
- `online` - Service is running and accessible
- `offline` - Service is not accessible
- `available` - Feature is installed and ready
- `unavailable` - Feature is not installed

---

### POST `/chat`
Send text message to Lucy

**Request Body:**
```json
{
  "user_id": "default",
  "message": "Hello Lucy!",
  "temperature": 0.8,
  "max_tokens": 200
}
```

**Parameters:**
- `user_id` (string, optional): User identifier for conversation tracking. Default: "default"
- `message` (string, required): Text message to send
- `temperature` (float, optional): LLM temperature (0.0-1.0). Default: 0.8
- `max_tokens` (int, optional): Maximum tokens in response. Default: 200

**Response:**
```json
{
  "expressions": ["smile", "giggle"],
  "text": "Hi there! I'm so happy to see you!",
  "audio_url": "/audio/tts_1234567890_abc12345.wav",
  "raw_response": "*smile*\nHi there! I'm so happy to see you!\n*giggle*"
}
```

**Response Fields:**
- `expressions` (array): List of expression tags extracted from response
- `text` (string): Clean text with expressions removed
- `audio_url` (string, nullable): URL to synthesized audio file (if TTS enabled)
- `raw_response` (string): Raw LLM response with expression tags

**Status Codes:**
- `200` - Success
- `400` - Invalid request (empty message, etc.)
- `503` - LLM service unavailable
- `500` - Internal server error

---

### POST `/speech`
Send speech audio to Lucy (with automatic transcription)

**Request:** Multipart form data
- `audio` (file, required): Audio file (WAV, MP3, OGG, FLAC)
- `user_id` (string, optional): User identifier. Default: "default"
- `temperature` (float, optional): LLM temperature. Default: 0.8
- `max_tokens` (int, optional): Maximum tokens. Default: 200

**Example using curl:**
```bash
curl -X POST http://localhost:8000/speech \
  -F "audio=@recording.wav" \
  -F "user_id=default" \
  -F "temperature=0.8"
```

**Response:** Same as `/chat` endpoint

**Status Codes:**
- `200` - Success
- `400` - Invalid audio file
- `503` - STT service unavailable
- `500` - Internal server error

**Notes:**
- Maximum audio file size: 10 MB
- Recommended sample rate: 16kHz for best STT performance
- Supported formats: WAV (preferred), MP3, OGG, FLAC

---

### DELETE `/conversation/{user_id}`
Clear conversation history for a user

**Parameters:**
- `user_id` (path parameter): User identifier

**Example:**
```bash
curl -X DELETE http://localhost:8000/conversation/default
```

**Response:**
```json
{
  "message": "Conversation history cleared for default"
}
```

---

### GET `/conversation/{user_id}`
Get conversation history for a user

**Parameters:**
- `user_id` (path parameter): User identifier

**Example:**
```bash
curl http://localhost:8000/conversation/default
```

**Response:**
```json
{
  "user_id": "default",
  "history": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "*smile*\nHi there!"
    }
  ],
  "metadata": {
    "created_at": "2024-02-11T10:30:00",
    "last_updated": "2024-02-11T10:31:00",
    "message_count": 2
  },
  "exchange_count": 1
}
```

---

### GET `/audio/{filename}`
Retrieve generated audio file

**Parameters:**
- `filename` (path parameter): Audio filename returned in chat/speech response

**Example:**
```bash
curl http://localhost:8000/audio/tts_1234567890_abc12345.wav --output response.wav
```

**Response:** Audio file (WAV format)

---

## Expression Tags

Lucy uses expression tags to convey emotions. These are automatically:
1. Extracted from the response
2. Removed from the TTS text
3. Returned in the `expressions` array

### Supported Expressions

| Expression | Description | Unity Animation |
|-----------|-------------|-----------------|
| `*smile*` | Happy, warm | Joy blend shape |
| `*smirk*` | Confident, sly | Fun blend shape |
| `*giggle*` | Playful laugh | Joy blend shape |
| `*laugh*` | Full laugh | Joy blend shape |
| `*pout*` | Sad, disappointed | Sorrow blend shape |
| `*blush*` | Shy, embarrassed | Joy blend shape |
| `*shy*` | Timid, hesitant | Sorrow blend shape |
| `*angry*` | Angry, annoyed | Angry blend shape |
| `*excited*` | Surprised, energetic | Joy blend shape |
| `*surprised*` | Shocked | Surprised blend shape |
| `*thinking*` | Contemplative | Neutral blend shape |
| `*happy*` | Joyful | Joy blend shape |
| `*sad*` | Melancholic | Sorrow blend shape |
| `*worried*` | Concerned | Sorrow blend shape |
| `*confused*` | Puzzled | Surprised blend shape |

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message description"
}
```

### Common Errors

**400 Bad Request:**
```json
{
  "detail": "Empty text input"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "LLM service error: Connection refused"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error: [error details]"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented for local development.

For production deployment, consider:
- Rate limiting per user_id
- Maximum conversation history per user
- Audio file cleanup policies

---

## Configuration

### LLM Parameters

Adjust these in your request for different behavior:

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| temperature | 0.0-1.0 | 0.8 | Higher = more creative/random |
| max_tokens | 1-512 | 200 | Maximum response length |

**Recommended Settings:**
- Casual chat: `temperature=0.8`
- Factual responses: `temperature=0.3`
- Creative storytelling: `temperature=0.9`

### Conversation Memory

- Default: Last 6 exchanges (12 messages) kept
- Configurable in `backend/config.py`
- Automatic trimming on each message

---

## WebSocket Support (Future)

WebSocket support is planned for:
- Real-time streaming responses
- Live audio streaming
- Bi-directional communication

Stay tuned for updates!

---

## Examples

### Python Client
```python
import requests

# Text chat
response = requests.post("http://localhost:8000/chat", json={
    "user_id": "alice",
    "message": "Tell me a joke",
    "temperature": 0.8
})

data = response.json()
print(f"Lucy says: {data['text']}")
print(f"Expressions: {data['expressions']}")
```

### Unity/C#
```csharp
using UnityEngine;
using Lucy;

public class Example : MonoBehaviour
{
    private VirtualCompanionController lucy;
    
    void Start()
    {
        lucy = FindObjectOfType<VirtualCompanionController>();
        lucy.OnResponseReceived += OnResponse;
        lucy.SendMessage("Hello Lucy!");
    }
    
    void OnResponse(CompanionResponse response)
    {
        Debug.Log($"Lucy: {response.text}");
        Debug.Log($"Expressions: {string.Join(", ", response.expressions)}");
    }
}
```

### JavaScript/Fetch
```javascript
async function sendMessage(message) {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: 'web_user',
            message: message,
            temperature: 0.8
        })
    });
    
    const data = await response.json();
    console.log('Lucy:', data.text);
    console.log('Expressions:', data.expressions);
    
    // Play audio if available
    if (data.audio_url) {
        const audio = new Audio('http://localhost:8000' + data.audio_url);
        audio.play();
    }
}
```

---

## Support

For issues or questions:
- Check logs in `backend/` directory
- Verify llama.cpp server is running
- Test endpoints with curl or Postman
- Review error messages in response `detail` field
