"""
Text-to-Speech Engine
Supports OpenVoice (primary) and Piper TTS (fallback)
"""

from pathlib import Path
import re
from typing import List, Tuple
import subprocess


class TTSEngine:
    def __init__(self, engine: str = "piper", voice: str = "en_US-lessac-medium"):
        """Initialize TTS Engine
        
        Args:
            engine: "piper" or "openvoice"
            voice: Voice model to use
        """
        self.engine = engine
        self.voice = voice
        
        # Expression to audio effect mapping
        self.expression_effects = {
            "smile": "warm",
            "smirk": "confident",
            "giggle": "playful",
            "pout": "gentle",
            "blush": "shy",
            "shy": "soft",
            "angry": "firm",
            "excited": "energetic"
        }
    
    def clean_text_for_tts(self, text: str, expressions: List[str]) -> str:
        """Remove expression tags and prepare text for TTS
        Also handles expression-aware tone adjustments
        
        Args:
            text: Clean text without expression tags
            expressions: List of detected expressions
        
        Returns:
            TTS-ready text
        """
        # Remove any remaining asterisks
        text = re.sub(r"\*.*?\*", "", text)
        
        # TODO: Add SSML tags for emotion control if using advanced TTS
        # Example: <prosody rate="fast" pitch="+5%">text</prosody>
        
        return text.strip()
    
    def synthesize_piper(self, text: str, output_path: str) -> str:
        """Synthesize speech using Piper TTS
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
        
        Returns:
            Path to generated audio file
        """
        # Piper TTS command
        # Install: pip install piper-tts
        # Download models from: https://github.com/rhasspy/piper
        
        cmd = [
            "piper",
            "--model", self.voice,
            "--output_file", output_path
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=text.encode())
            
            if process.returncode != 0:
                raise Exception(f"Piper TTS error: {stderr.decode()}")
            
            return output_path
        
        except Exception as e:
            raise Exception(f"TTS synthesis failed: {str(e)}")
    
    def synthesize_openvoice(self, text: str, output_path: str, emotion: str = "neutral") -> str:
        """Synthesize speech using OpenVoice with emotion control
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
            emotion: Emotion tag for voice modulation
        
        Returns:
            Path to generated audio file
        """
        # TODO: Integrate OpenVoice
        # https://github.com/myshell-ai/OpenVoice
        
        raise NotImplementedError("OpenVoice integration pending")
    
    def synthesize(self, text: str, expressions: List[str], output_path: str) -> str:
        """Main synthesis method with expression awareness
        
        Args:
            text: Clean text to synthesize
            expressions: List of expressions for tone control
            output_path: Output audio file path
        
        Returns:
            Path to generated audio file
        """
        # Clean text for TTS
        clean_text = self.clean_text_for_tts(text, expressions)
        
        # Determine primary emotion
        emotion = "neutral"
        if expressions:
            emotion = self.expression_effects.get(expressions[0], "neutral")
        
        # Route to appropriate engine
        if self.engine == "piper":
            return self.synthesize_piper(clean_text, output_path)
        elif self.engine == "openvoice":
            return self.synthesize_openvoice(clean_text, output_path, emotion)
        else:
            raise ValueError(f"Unknown TTS engine: {self.engine}")


# Example usage
if __name__ == "__main__":
    tts = TTSEngine(engine="piper")
    
    text = "Oh really? You think you can beat me? That's cute."
    expressions = ["smirk", "giggle"]
    
    # output = tts.synthesize(text, expressions, "output.wav")
    # print(f"Audio generated: {output}")