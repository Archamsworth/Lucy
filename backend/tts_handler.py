"""
TTS Handler for Lucy AI Companion
Handles text-to-speech synthesis with expression awareness
"""

from pathlib import Path
from typing import List, Optional
import hashlib
import time


class TTSHandler:
    """Handle TTS synthesis with expression-aware voice modulation"""
    
    def __init__(self, tts_engine, output_dir: str = "./audio_output"):
        """
        Initialize TTS handler
        
        Args:
            tts_engine: TTS engine instance
            output_dir: Directory for audio output files
        """
        self.tts_engine = tts_engine
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Cache for generated audio files
        self.cache = {}
    
    def synthesize(self, text: str, expressions: List[str], 
                  use_cache: bool = True) -> str:
        """
        Synthesize speech from text with expression awareness
        
        Args:
            text: Clean text to synthesize (expressions already removed)
            expressions: List of expressions for tone modulation
            use_cache: Whether to use cached audio if available
            
        Returns:
            Path to generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty text")
        
        # Generate cache key
        cache_key = self._generate_cache_key(text, expressions)
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached_path = self.cache[cache_key]
            if Path(cached_path).exists():
                return cached_path
        
        # Generate output filename
        timestamp = int(time.time() * 1000)
        output_filename = f"tts_{timestamp}_{cache_key[:8]}.wav"
        output_path = str(self.output_dir / output_filename)
        
        # Synthesize speech
        try:
            audio_path = self.tts_engine.synthesize(text, expressions, output_path)
            
            # Cache the result
            if use_cache:
                self.cache[cache_key] = audio_path
            
            return audio_path
            
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed: {str(e)}")
    
    def _generate_cache_key(self, text: str, expressions: List[str]) -> str:
        """
        Generate cache key for text and expressions
        
        Args:
            text: Text content
            expressions: List of expressions
            
        Returns:
            Cache key (hash)
        """
        content = f"{text}|{','.join(expressions)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def clean_text_for_tts(self, text: str) -> str:
        """
        Additional text cleaning for TTS
        
        Args:
            text: Text to clean
            
        Returns:
            TTS-ready text
        """
        # Remove any remaining special characters that might confuse TTS
        text = text.replace("*", "")
        text = text.replace("_", "")
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        return text
    
    def clear_cache(self):
        """Clear the audio cache"""
        self.cache.clear()
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old audio files
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for audio_file in self.output_dir.glob("tts_*.wav"):
            file_age = current_time - audio_file.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    audio_file.unlink()
                except Exception:
                    pass
    
    def get_audio_url(self, audio_path: str, base_url: str) -> str:
        """
        Convert local audio path to URL
        
        Args:
            audio_path: Local file path
            base_url: Base URL for API
            
        Returns:
            Full URL to audio file
        """
        filename = Path(audio_path).name
        return f"{base_url}/audio/{filename}"


# Example usage
if __name__ == "__main__":
    # Mock TTS engine for testing
    class MockTTSEngine:
        def synthesize(self, text, expressions, output_path):
            Path(output_path).touch()
            return output_path
    
    handler = TTSHandler(MockTTSEngine(), "./test_audio_output")
    
    # Test synthesis
    try:
        audio_path = handler.synthesize(
            "Hello there! How are you?",
            ["smile", "happy"]
        )
        print(f"Generated audio: {audio_path}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test cache key generation
    key1 = handler._generate_cache_key("test", ["smile"])
    key2 = handler._generate_cache_key("test", ["smile"])
    print(f"\nCache keys match: {key1 == key2}")
