"""
Unit tests for WakeWordDetector module
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wake_word import WakeWordDetector


class TestWakeWordDetector(unittest.TestCase):
    """Test cases for WakeWordDetector"""

    def setUp(self):
        """Set up detector with default wake words"""
        self.detector = WakeWordDetector()

    # ------------------------------------------------------------------
    # detect() – text matching
    # ------------------------------------------------------------------

    def test_detect_hey_lucy(self):
        """'hey lucy' should be detected"""
        self.assertTrue(self.detector.detect("hey lucy, what's the weather?"))

    def test_detect_hi_lucy(self):
        """'hi lucy' should be detected"""
        self.assertTrue(self.detector.detect("hi lucy how are you"))

    def test_detect_ok_lucy(self):
        """'ok lucy' should be detected"""
        self.assertTrue(self.detector.detect("ok lucy tell me a story"))

    def test_detect_okay_lucy(self):
        """'okay lucy' should be detected"""
        self.assertTrue(self.detector.detect("okay lucy play some music"))

    def test_detect_hey_luce(self):
        """'hey luce' should be detected"""
        self.assertTrue(self.detector.detect("hey luce are you there"))

    def test_no_detection_without_wake_word(self):
        """Random speech without wake word should not trigger"""
        self.assertFalse(self.detector.detect("what is the weather like today?"))
        self.assertFalse(self.detector.detect("I love you"))
        self.assertFalse(self.detector.detect("hello there general kenobi"))

    def test_detect_empty_string(self):
        """Empty string should return False"""
        self.assertFalse(self.detector.detect(""))

    def test_detect_none_like_empty(self):
        """None-equivalent empty string should return False"""
        self.assertFalse(self.detector.detect(""))

    def test_detect_case_insensitive(self):
        """Detection should be case-insensitive"""
        self.assertTrue(self.detector.detect("HEY LUCY can you help me?"))
        self.assertTrue(self.detector.detect("Hey Lucy!"))

    def test_detect_strips_punctuation(self):
        """Punctuation in transcription should not prevent detection"""
        self.assertTrue(self.detector.detect("hey, lucy! how are you?"))

    def test_detect_mid_sentence(self):
        """Wake word embedded mid-sentence should still be detected"""
        self.assertTrue(self.detector.detect("I said hey lucy what do you think"))

    # ------------------------------------------------------------------
    # Custom wake words
    # ------------------------------------------------------------------

    def test_custom_wake_words(self):
        """Custom wake words should be used"""
        detector = WakeWordDetector(wake_words=["hello world", "wake up"])
        self.assertTrue(detector.detect("hello world this is a test"))
        self.assertTrue(detector.detect("wake up please"))
        self.assertFalse(detector.detect("hey lucy"))

    def test_add_wake_word(self):
        """Adding a wake word should make it detectable"""
        self.detector.add_wake_word("yo lucy")
        self.assertTrue(self.detector.detect("yo lucy what's up"))

    def test_add_wake_word_case_normalised(self):
        """Added wake words should be lowercased"""
        self.detector.add_wake_word("YO LUCY")
        self.assertIn("yo lucy", self.detector.get_wake_words())

    def test_add_duplicate_wake_word(self):
        """Adding a duplicate should not create duplicates"""
        initial_count = len(self.detector.get_wake_words())
        self.detector.add_wake_word("hey lucy")
        self.assertEqual(len(self.detector.get_wake_words()), initial_count)

    def test_remove_wake_word(self):
        """Removing a wake word should prevent detection"""
        self.detector.remove_wake_word("hey lucy")
        self.assertFalse(self.detector.detect("hey lucy are you there"))

    def test_remove_nonexistent_wake_word(self):
        """Removing a non-existent wake word should not raise"""
        try:
            self.detector.remove_wake_word("nonexistent phrase")
        except Exception as e:
            self.fail(f"remove_wake_word raised unexpectedly: {e}")

    def test_get_wake_words_returns_copy(self):
        """get_wake_words should return a copy, not the internal list"""
        words = self.detector.get_wake_words()
        words.append("tampered")
        self.assertNotIn("tampered", self.detector.get_wake_words())

    # ------------------------------------------------------------------
    # detect_from_audio()
    # ------------------------------------------------------------------

    def test_detect_from_audio_requires_stt_engine(self):
        """detect_from_audio should raise ValueError if no STT engine"""
        detector = WakeWordDetector(stt_engine=None)
        with self.assertRaises(ValueError):
            detector.detect_from_audio("/tmp/fake.wav")

    def test_detect_from_audio_delegates_to_stt(self):
        """detect_from_audio should call stt_engine.transcribe and then detect"""
        mock_stt = MagicMock()
        mock_stt.transcribe.return_value = "hey lucy what's up"

        detector = WakeWordDetector(stt_engine=mock_stt)
        result = detector.detect_from_audio("/fake/path.wav")

        mock_stt.transcribe.assert_called_once_with("/fake/path.wav")
        self.assertTrue(result)

    def test_detect_from_audio_no_wake_word(self):
        """detect_from_audio returns False when transcription has no wake word"""
        mock_stt = MagicMock()
        mock_stt.transcribe.return_value = "this is just random speech"

        detector = WakeWordDetector(stt_engine=mock_stt)
        result = detector.detect_from_audio("/fake/path.wav")

        self.assertFalse(result)

    # ------------------------------------------------------------------
    # set_stt_engine()
    # ------------------------------------------------------------------

    def test_set_stt_engine(self):
        """set_stt_engine should update the engine"""
        mock_stt = MagicMock()
        self.detector.set_stt_engine(mock_stt)
        self.assertIs(self.detector.stt_engine, mock_stt)

    # ------------------------------------------------------------------
    # Default wake words
    # ------------------------------------------------------------------

    def test_default_wake_words_are_present(self):
        """Default wake words list should include expected phrases"""
        defaults = self.detector.get_wake_words()
        self.assertIn("hey lucy", defaults)
        self.assertIn("hi lucy", defaults)
        self.assertIn("ok lucy", defaults)


if __name__ == "__main__":
    unittest.main()
