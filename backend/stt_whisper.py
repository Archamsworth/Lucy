"""
Speech-to-Text using faster-whisper
Optimized for real-time performance
"""

from faster_whisper import WhisperModel
import numpy as np
from pathlib import Path
import tempfile


class WhisperSTT:
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        """Initialize Whisper STT
        
        Args:
            model_size: "tiny", "base", "small", "medium", "large-v2"
            device: "cpu" or "cuda"
            compute_type: "int8", "float16", "float32"
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper model loaded!")
    
    def transcribe(self, audio_path: str, language: str = "en") -> str:
        """Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "en")
        
        Returns:
            Transcribed text
        """
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    def transcribe_realtime(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio data in real-time
        
        Args:
            audio_data: NumPy array of audio samples
            sample_rate: Sample rate of audio
        
        Returns:
            Transcribed text
        """
        # Save to temporary file (faster-whisper requires file input)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            import scipy.io.wavfile as wavfile
            wavfile.write(tmp_file.name, sample_rate, audio_data)
            result = self.transcribe(tmp_file.name)
            Path(tmp_file.name).unlink()  # Clean up
        
        return result


# Example usage
if __name__ == "__main__":
    stt = WhisperSTT(model_size="small", device="cpu")
    
    # Test with audio file
    # result = stt.transcribe("test_audio.wav")
    # print(f"Transcription: {result}")