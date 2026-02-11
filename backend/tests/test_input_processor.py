"""
Unit tests for Input Processor
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from input_processor import InputProcessor


class TestInputProcessor(unittest.TestCase):
    """Test cases for InputProcessor"""
    
    def setUp(self):
        """Set up test processor"""
        self.processor = InputProcessor()
    
    def test_process_text_basic(self):
        """Test basic text processing"""
        text = "Hello there!"
        processed = self.processor.process_text(text)
        self.assertEqual(processed, "Hello there!")
    
    def test_process_text_whitespace(self):
        """Test whitespace normalization"""
        text = "  Hello   there!  "
        processed = self.processor.process_text(text)
        self.assertEqual(processed, "Hello there!")
    
    def test_process_text_multiple_spaces(self):
        """Test multiple space normalization"""
        text = "Hello    there    friend"
        processed = self.processor.process_text(text)
        self.assertEqual(processed, "Hello there friend")
    
    def test_process_text_empty_raises(self):
        """Test that empty text raises error"""
        with self.assertRaises(ValueError):
            self.processor.process_text("")
    
    def test_process_text_whitespace_only_raises(self):
        """Test that whitespace-only text raises error"""
        with self.assertRaises(ValueError):
            self.processor.process_text("   \n  \t  ")
    
    def test_process_text_too_long_raises(self):
        """Test that too long text raises error"""
        text = "x" * 1001
        with self.assertRaises(ValueError):
            self.processor.process_text(text)
    
    def test_process_text_max_length_ok(self):
        """Test that max length text is OK"""
        text = "x" * 1000
        processed = self.processor.process_text(text)
        self.assertEqual(len(processed), 1000)
    
    def test_validate_audio_valid(self):
        """Test audio validation with valid data"""
        audio_data = b"fake audio data" * 100
        result = self.processor.validate_audio(audio_data)
        self.assertTrue(result)
    
    def test_validate_audio_too_large(self):
        """Test audio validation with too large file"""
        # Create 11 MB of fake data
        audio_data = b"x" * (11 * 1024 * 1024)
        with self.assertRaises(ValueError):
            self.processor.validate_audio(audio_data, max_size_mb=10.0)
    
    def test_validate_audio_too_small(self):
        """Test audio validation with too small file"""
        audio_data = b"x"
        with self.assertRaises(ValueError):
            self.processor.validate_audio(audio_data)
    
    def test_process_speech_without_stt_raises(self):
        """Test that speech processing without STT raises error"""
        audio_data = b"fake audio data"
        with self.assertRaises(ValueError):
            self.processor.process_speech(audio_data)
    
    def test_set_stt_engine(self):
        """Test setting STT engine"""
        class MockSTT:
            pass
        
        mock_stt = MockSTT()
        self.processor.set_stt_engine(mock_stt)
        self.assertEqual(self.processor.stt_engine, mock_stt)


if __name__ == "__main__":
    unittest.main()
