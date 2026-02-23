"""
Wake word detection for Lucy AI Companion
Detects activation phrases ("hey lucy", "hi lucy", etc.) in transcribed speech
"""

import re
from typing import List, Optional


class WakeWordDetector:
    """
    Detects wake words by matching keyword phrases against Whisper transcriptions.

    This lightweight approach reuses the existing Whisper STT engine rather than
    requiring a separate always-on wake-word binary, keeping resource usage low
    on consumer hardware.
    """

    DEFAULT_WAKE_WORDS: List[str] = [
        "hey lucy",
        "hi lucy",
        "ok lucy",
        "okay lucy",
        "hey luce",
    ]

    def __init__(
        self,
        wake_words: Optional[List[str]] = None,
        stt_engine=None,
    ):
        """
        Initialize wake word detector

        Args:
            wake_words: Custom list of wake word phrases (uses defaults if None)
            stt_engine: WhisperSTT instance for transcribing audio files
        """
        self.wake_words: List[str] = (
            [w.lower().strip() for w in wake_words]
            if wake_words is not None
            else list(self.DEFAULT_WAKE_WORDS)
        )
        self.stt_engine = stt_engine

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------

    def detect(self, transcription: str) -> bool:
        """
        Check whether a transcription contains a wake word phrase

        Args:
            transcription: Text produced by STT transcription

        Returns:
            True if any wake word is found in the transcription
        """
        if not transcription:
            return False

        # Normalise: lower-case and strip punctuation for fuzzy matching
        text_clean = re.sub(r"[^a-z0-9\s]", "", transcription.lower())

        for wake_word in self.wake_words:
            if wake_word in text_clean:
                return True

        return False

    def detect_from_audio(self, audio_path: str) -> bool:
        """
        Transcribe an audio file and detect the wake word in the result

        Args:
            audio_path: Path to the audio file (WAV, MP3, etc.)

        Returns:
            True if the wake word is detected

        Raises:
            ValueError: If no STT engine has been configured
        """
        if self.stt_engine is None:
            raise ValueError(
                "STT engine not configured. Pass a WhisperSTT instance to WakeWordDetector."
            )

        transcription = self.stt_engine.transcribe(audio_path)
        return self.detect(transcription)

    # ------------------------------------------------------------------
    # Wake word management
    # ------------------------------------------------------------------

    def get_wake_words(self) -> List[str]:
        """Return a copy of the current wake word list"""
        return self.wake_words.copy()

    def add_wake_word(self, wake_word: str) -> None:
        """
        Add a new wake word phrase

        Args:
            wake_word: Phrase to add (case-insensitive)
        """
        normalised = wake_word.lower().strip()
        if normalised not in self.wake_words:
            self.wake_words.append(normalised)

    def remove_wake_word(self, wake_word: str) -> None:
        """
        Remove a wake word phrase

        Args:
            wake_word: Phrase to remove (case-insensitive)
        """
        normalised = wake_word.lower().strip()
        if normalised in self.wake_words:
            self.wake_words.remove(normalised)

    def set_stt_engine(self, stt_engine) -> None:
        """
        Set or replace the STT engine

        Args:
            stt_engine: WhisperSTT instance
        """
        self.stt_engine = stt_engine


# Example usage
if __name__ == "__main__":
    detector = WakeWordDetector()

    samples = [
        "hey lucy, what's the weather today?",
        "hi there, how are you?",
        "ok lucy please help me",
        "random speech without a trigger",
    ]

    for text in samples:
        detected = detector.detect(text)
        print(f"{'✓' if detected else '✗'}  '{text}'")
