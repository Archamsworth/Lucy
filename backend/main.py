"""
Lucy AI Virtual Companion - FastAPI Backend
Handles LLM inference, STT, TTS, and expression parsing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
import re
import json
from pathlib import Path
import tempfile
import os
from typing import List, Optional

app = FastAPI(title="Lucy AI Companion API")

# CORS middleware for Unity integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LLAMA_CPP_URL = "http://localhost:8001/v1/chat/completions"
MAX_HISTORY = 6  # Keep last 6 conversation exchanges

# System prompt with expression tagging
SYSTEM_PROMPT = """You are Lucy, a virtual companion.
You speak naturally and emotionally.

Rules:
- Always express emotions using captions like:
  *smile*
  *smirk*
  *pout*
  *giggle*
  *blush*
  *shy*
  *angry*
  *excited*
- Put expression captions on separate lines.
- Do NOT describe emotions in plain text.
- Keep responses short and conversational.
- Speak like a real human in real-time chat.
- Be warm, friendly, and engaging.
"""

# Conversation memory (in production, use Redis or database)
conversation_history = {}


class TextInput(BaseModel):
    user_id: str = "default"
    message: str
    temperature: float = 0.8
    max_tokens: int = 200


class ConversationResponse(BaseModel):
    expressions: List[str]
    text: str
    audio_path: Optional[str] = None
    raw_response: str


def parse_expression_output(text: str) -> tuple[List[str], str]:
    """
    Extract expressions and clean text from model output
    
    Example input:
    *smirk*
    Oh really? You think you can beat me?
    *giggle*
    That's cute.
    
    Returns: (['smirk', 'giggle'], "Oh really? You think you can beat me? That's cute.")
    """
    expressions = re.findall(r"\*(.*?)\*", text)
    clean_text = re.sub(r"\*(.*?)\*", "", text).strip()
    # Remove extra whitespace and newlines
    clean_text = " ".join(clean_text.split())
    return expressions, clean_text


def get_conversation_history(user_id: str) -> List[dict]:
    """Get conversation history for a user"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]


def update_conversation_history(user_id: str, role: str, content: str):
    """Update conversation history, maintaining max length"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({"role": role, "content": content})
    
    # Keep only last MAX_HISTORY exchanges (user + assistant pairs)
    if len(conversation_history[user_id]) > MAX_HISTORY * 2:
        conversation_history[user_id] = conversation_history[user_id][-(MAX_HISTORY * 2):]


def query_llm(messages: List[dict], temperature: float = 0.8, max_tokens: int = 200) -> str:
    """Query the llama.cpp server"""
    try:
        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.9,
            "max_tokens": max_tokens,
            "repeat_penalty": 1.1,
            "stream": False
        }
        
        response = requests.post(LLAMA_CPP_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Lucy AI Companion API", "status": "online"}


@app.get("/health")
async def health_check():
    """Check if all services are running"""
    try:
        # Test llama.cpp connection
        response = requests.get(f"http://localhost:8001/health", timeout=5)
        llm_status = "online" if response.status_code == 200 else "offline"
    except:
        llm_status = "offline"
    
    return {
        "api": "online",
        "llm": llm_status
    }


@app.post("/chat", response_model=ConversationResponse)
async def chat(input_data: TextInput):
    """Main chat endpoint
    Handles text input and returns expressions + clean text"""
    user_id = input_data.user_id
    user_message = input_data.message
    
    # Get conversation history
    history = get_conversation_history(user_id)
    
    # Build messages for LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    
    # Query LLM
    response = query_llm(messages, input_data.temperature, input_data.max_tokens)
    
    # Parse expressions and clean text
    expressions, clean_text = parse_expression_output(response)
    
    # Update conversation history
    update_conversation_history(user_id, "user", user_message)
    update_conversation_history(user_id, "assistant", response)
    
    return ConversationResponse(
        expressions=expressions,
        text=clean_text,
        audio_path=None,  # TTS integration point
        raw_response=response
    )


@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text using Whisper
    TODO: Integrate faster-whisper
    """
    # Placeholder for Whisper integration
    return JSONResponse(
        status_code=501,
        content={"message": "STT integration pending - integrate faster-whisper here"}
    )


@app.post("/text-to-speech")
async def text_to_speech(text: str):
    """Convert text to speech
    TODO: Integrate OpenVoice or Piper TTS
    """
    # Placeholder for TTS integration
    return JSONResponse(
        status_code=501,
        content={"message": "TTS integration pending - integrate OpenVoice/Piper here"}
    )


@app.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str):
    """Clear conversation history for a user"""
    if user_id in conversation_history:
        conversation_history[user_id] = []
    return {"message": f"Conversation history cleared for {user_id}"}


@app.get("/conversation/{user_id}")
async def get_conversation(user_id: str):
    """Get conversation history for a user"""
    return {
        "user_id": user_id,
        "history": get_conversation_history(user_id)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)