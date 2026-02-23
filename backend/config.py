"""
Configuration file for Lucy AI Companion
"""

import os
from pathlib import Path

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# LLM Configuration
LLAMA_CPP_HOST = os.getenv("LLAMA_CPP_HOST", "localhost")
LLAMA_CPP_PORT = int(os.getenv("LLAMA_CPP_PORT", "8001"))
LLAMA_CPP_URL = f"http://{LLAMA_CPP_HOST}:{LLAMA_CPP_PORT}/v1/chat/completions"

# Model Settings
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 200
DEFAULT_REPEAT_PENALTY = 1.1

# Conversation Settings
MAX_CONVERSATION_HISTORY = 6  # Keep last N exchanges

# STT Configuration
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")  # tiny, base, small, medium
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")  # cpu or cuda
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")  # int8, float16, float32

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "piper")  # piper or openvoice
TTS_VOICE = os.getenv("TTS_VOICE", "en_US-lessac-medium")

# File Storage
BASE_DIR = Path(__file__).parent
AUDIO_OUTPUT_DIR = BASE_DIR / "audio_output"
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

# RAG Configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
RAG_MAX_RESULTS = int(os.getenv("RAG_MAX_RESULTS", "3"))
RAG_SNIPPET_MAX_CHARS = int(os.getenv("RAG_SNIPPET_MAX_CHARS", "300"))

# Wake Word Configuration
WAKE_WORDS = [w.strip() for w in os.getenv("WAKE_WORDS", "hey lucy,hi lucy,ok lucy,okay lucy").split(",")]

# System Prompt
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

# Expression Mapping
EXPRESSION_EMOTIONS = {
    "smile": "warm",
    "smirk": "confident",
    "giggle": "playful",
    "pout": "gentle",
    "blush": "shy",
    "shy": "soft",
    "angry": "firm",
    "excited": "energetic",
    "happy": "joyful",
    "sad": "melancholic"
}