"""
Input Processor for Lucy AI Companion
Handles text and speech input processing
"""

from typing import Optional, Tuple
import tempfile
from pathlib import Path
import io


class InputProcessor:
    """Process text and speech inputs"""
    
    def __init__(self, stt_engine=None):
        """
        Initialize input processor
        
        Args:
            stt_engine: Speech-to-text engine instance (optional)
        """
        self.stt_engine = stt_engine
    
    def process_text(self, text: str) -> str:
        """
        Process text input
        
        Args:
            text: Raw text input from user
            
        Returns:
            Cleaned and processed text
        """
        # Basic text cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Basic validation
        if not text:
            raise ValueError("Empty text input")
        
        if len(text) > 1000:
            raise ValueError("Text too long (max 1000 characters)")
        
        return text
    
    def process_speech(self, audio_data: bytes, 
                      filename: Optional[str] = None) -> str:
        """
        Process speech input using STT
        
        Args:
            audio_data: Audio file data (bytes)
            filename: Original filename for format detection
            
        Returns:
            Transcribed text
            
        Raises:
            ValueError: If STT engine not configured or audio invalid
        """
        if self.stt_engine is None:
            raise ValueError("STT engine not configured")
        
        # Detect audio format from filename
        audio_format = "wav"  # default
        if filename:
            ext = Path(filename).suffix.lower()
            if ext in [".wav", ".mp3", ".ogg", ".flac"]:
                audio_format = ext[1:]  # remove dot
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f".{audio_format}", 
            delete=False
        ) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe audio
            text = self.stt_engine.transcribe(tmp_path)
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
            if not text or not text.strip():
                raise ValueError("No speech detected in audio")
            
            return text.strip()
            
        except Exception as e:
            # Clean up temp file on error
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()
            raise ValueError(f"Speech transcription failed: {str(e)}")
    
    def validate_audio(self, audio_data: bytes, 
                      max_size_mb: float = 10.0) -> bool:
        """
        Validate audio file
        
        Args:
            audio_data: Audio file data
            max_size_mb: Maximum file size in MB
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If audio is invalid
        """
        size_mb = len(audio_data) / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise ValueError(
                f"Audio file too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"
            )
        
        if len(audio_data) < 100:
            raise ValueError("Audio file too small or corrupted")
        
        return True
    
    def set_stt_engine(self, stt_engine):
        """
        Set or update STT engine
        
        Args:
            stt_engine: STT engine instance
        """
        self.stt_engine = stt_engine


# Example usage
if __name__ == "__main__":
    processor = InputProcessor()
    
    # Test text processing
    text1 = "  Hello   there!  "
    processed1 = processor.process_text(text1)
    print(f"Text input: {text1!r}")
    print(f"Processed: {processed1!r}")
    print()
    
    # Test validation
    try:
        processor.process_text("")
    except ValueError as e:
        print(f"Empty text error: {e}")
    
    try:
        processor.process_text("x" * 1001)
    except ValueError as e:
        print(f"Too long error: {e}")
    
    # Test speech without STT engine
    try:
        processor.process_speech(b"fake audio data")
    except ValueError as e:
        print(f"No STT engine error: {e}")
