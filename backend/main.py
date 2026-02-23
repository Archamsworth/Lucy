"""
Lucy AI Virtual Companion - FastAPI Backend
Handles LLM inference, STT, TTS, and expression parsing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
from typing import List, Optional
import traceback

# Import modular components
from config import (
    LLAMA_CPP_URL, MAX_CONVERSATION_HISTORY, SYSTEM_PROMPT,
    AUDIO_OUTPUT_DIR, WHISPER_MODEL_SIZE, WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE, TTS_ENGINE, TTS_VOICE,
    RAG_ENABLED, RAG_MAX_RESULTS, RAG_SNIPPET_MAX_CHARS,
    WAKE_WORDS
)
from llm_client import LLMClient, LLMConfig
from conversation_manager import ConversationManager
from expression_parser import ExpressionParser
from input_processor import InputProcessor
from tts_handler import TTSHandler
from rag_web_search import WebRAG
from wake_word import WakeWordDetector

# Optional imports for STT/TTS
try:
    from stt_whisper import WhisperSTT
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: faster-whisper not installed. STT will be unavailable.")

try:
    from tts_engine import TTSEngine
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: TTS engine not available. Audio responses will be disabled.")

# Initialize FastAPI app
app = FastAPI(
    title="Lucy AI Companion API",
    description="Real-time virtual companion with emotion-aware responses",
    version="1.0.0"
)

# CORS middleware for Unity integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio serving
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_OUTPUT_DIR)), name="audio")

# Initialize components
llm_client = LLMClient(LLMConfig(url=LLAMA_CPP_URL))
conversation_manager = ConversationManager(max_history=MAX_CONVERSATION_HISTORY)
expression_parser = ExpressionParser()

# Initialize RAG
rag = WebRAG(max_results=RAG_MAX_RESULTS, snippet_max_chars=RAG_SNIPPET_MAX_CHARS)
if RAG_ENABLED and rag.is_available:
    print("✓ Web RAG initialized (DuckDuckGo)")
elif RAG_ENABLED:
    print("Warning: RAG enabled but duckduckgo-search not installed. Install with: pip install duckduckgo-search")

# Initialize STT if available
stt_engine = None
if WHISPER_AVAILABLE:
    try:
        stt_engine = WhisperSTT(
            model_size=WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print(f"✓ Whisper STT initialized ({WHISPER_MODEL_SIZE})")
    except Exception as e:
        print(f"Warning: Could not initialize Whisper: {e}")

input_processor = InputProcessor(stt_engine=stt_engine)

# Initialize wake word detector
wake_word_detector = WakeWordDetector(wake_words=WAKE_WORDS, stt_engine=stt_engine)
print(f"✓ Wake word detector initialized ({wake_word_detector.get_wake_words()})")

# Initialize TTS if available
tts_handler = None
if TTS_AVAILABLE:
    try:
        tts_engine = TTSEngine(engine=TTS_ENGINE, voice=TTS_VOICE)
        tts_handler = TTSHandler(tts_engine, output_dir=str(AUDIO_OUTPUT_DIR))
        print(f"✓ TTS initialized ({TTS_ENGINE})")
    except Exception as e:
        print(f"Warning: Could not initialize TTS: {e}")


class TextInput(BaseModel):
    user_id: str = "default"
    message: str
    temperature: float = 0.8
    max_tokens: int = 200


class SpeechInput(BaseModel):
    user_id: str = "default"
    temperature: float = 0.8
    max_tokens: int = 200


class ConversationResponse(BaseModel):
    expressions: List[str]
    text: str
    audio_url: Optional[str] = None
    raw_response: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Lucy AI Companion API",
        "status": "online",
        "version": "1.0.0",
        "features": {
            "chat": True,
            "stt": WHISPER_AVAILABLE,
            "tts": TTS_AVAILABLE,
            "rag": RAG_ENABLED and rag.is_available,
            "wake_word": True
        }
    }


@app.get("/health")
async def health_check():
    """Check if all services are running"""
    llm_healthy = llm_client.check_health()

    return {
        "api": "online",
        "llm": "online" if llm_healthy else "offline",
        "stt": "available" if WHISPER_AVAILABLE else "unavailable",
        "tts": "available" if TTS_AVAILABLE else "unavailable",
        "rag": "available" if (RAG_ENABLED and rag.is_available) else "unavailable"
    }


@app.post("/chat", response_model=ConversationResponse)
async def chat(input_data: TextInput):
    """
    Main chat endpoint - handles text input
    
    Processes text input, generates response with expressions,
    and optionally synthesizes audio
    """
    try:
        user_id = input_data.user_id

        # Process and validate input
        user_message = input_processor.process_text(input_data.message)

        # Optionally augment system prompt with web search context
        system_prompt = SYSTEM_PROMPT
        if RAG_ENABLED and rag.is_available:
            web_context = rag.augment_query(user_message)
            if web_context:
                system_prompt = f"{SYSTEM_PROMPT}\n\n{web_context}"

        # Build messages for LLM
        messages = conversation_manager.format_for_llm(
            user_id, system_prompt, user_message
        )
        
        # Query LLM
        response = llm_client.generate(
            messages,
            temperature=input_data.temperature,
            max_tokens=input_data.max_tokens
        )
        
        # Parse expressions and clean text
        expressions, clean_text = expression_parser.parse(response)
        
        # Update conversation history
        conversation_manager.add_message(user_id, "user", user_message)
        conversation_manager.add_message(user_id, "assistant", response)
        
        # Synthesize audio if TTS is available
        audio_url = None
        if tts_handler and clean_text:
            try:
                audio_path = tts_handler.synthesize(clean_text, expressions)
                # Convert to URL (assuming we're serving from /audio)
                audio_url = f"/audio/{Path(audio_path).name}"
            except Exception as e:
                print(f"TTS warning: {e}")
                # Continue without audio
        
        return ConversationResponse(
            expressions=expressions,
            text=clean_text,
            audio_url=audio_url,
            raw_response=response
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/speech", response_model=ConversationResponse)
async def speech(
    audio: UploadFile = File(...),
    user_id: str = "default",
    temperature: float = 0.8,
    max_tokens: int = 200
):
    """
    Speech input endpoint - handles audio input
    
    Transcribes speech to text, then processes like chat endpoint
    """
    if not WHISPER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Speech-to-text not available. Install faster-whisper."
        )
    
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Validate audio
        input_processor.validate_audio(audio_data)
        
        # Transcribe speech to text
        transcribed_text = input_processor.process_speech(
            audio_data,
            filename=audio.filename
        )
        
        # Process as text input
        input_data = TextInput(
            user_id=user_id,
            message=transcribed_text,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return await chat(input_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Speech error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str):
    """Clear conversation history for a user"""
    conversation_manager.clear_history(user_id)
    return {"message": f"Conversation history cleared for {user_id}"}


@app.get("/conversation/{user_id}")
async def get_conversation(user_id: str):
    """Get conversation history for a user"""
    return conversation_manager.export_history(user_id)


class RAGSearchRequest(BaseModel):
    query: str


@app.post("/rag_search")
async def rag_search(request: RAGSearchRequest):
    """
    Perform a web search and return formatted context for RAG

    Returns the top search results as a context string that can be
    used to augment an LLM prompt.
    """
    if not RAG_ENABLED or not rag.is_available:
        raise HTTPException(
            status_code=503,
            detail="Web RAG is unavailable. Install duckduckgo-search or set RAG_ENABLED=true."
        )

    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query must not be empty")

        results = rag.search(query)
        context = rag.format_context(results)

        return {
            "query": query,
            "results": [
                {"title": r.title, "body": r.body, "href": r.href}
                for r in results
            ],
            "context": context
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"RAG search error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/wake")
async def detect_wake_word(
    audio: UploadFile = File(...),
):
    """
    Wake word detection endpoint

    Accepts a short audio clip, transcribes it with Whisper, and returns
    whether a wake word phrase (e.g. "hey lucy") was detected.
    The Unity client polls this endpoint with short recorded chunks to
    enable hands-free voice activation.
    """
    if not WHISPER_AVAILABLE or stt_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Wake word detection requires Whisper STT. Install faster-whisper."
        )

    try:
        audio_data = await audio.read()
        input_processor.validate_audio(audio_data)

        transcribed = input_processor.process_speech(
            audio_data,
            filename=audio.filename
        )

        detected = wake_word_detector.detect(transcribed)

        return {
            "wake_word_detected": detected,
            "transcription": transcribed,
            "wake_words": wake_word_detector.get_wake_words()
        }

    except ValueError as e:
        # Expected cases: no speech detected or audio too small – treat as no wake word
        print(f"Wake word detection skipped (no speech): {e}")
        return {
            "wake_word_detected": False,
            "transcription": "",
            "wake_words": wake_word_detector.get_wake_words()
        }
    except Exception as e:
        print(f"Wake word error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)