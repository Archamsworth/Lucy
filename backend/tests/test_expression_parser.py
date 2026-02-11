"""
Unit tests for Expression Parser
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from expression_parser import ExpressionParser


class TestExpressionParser(unittest.TestCase):
    """Test cases for ExpressionParser"""
    
    def setUp(self):
        """Set up test parser"""
        self.parser = ExpressionParser()
    
    def test_single_expression(self):
        """Test parsing single expression"""
        text = "*smile* Hello there!"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smile"])
        self.assertEqual(clean, "Hello there!")
    
    def test_multiple_expressions(self):
        """Test parsing multiple expressions"""
        text = "*smile*\nHello there!\n*giggle*\nHow are you?"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smile", "giggle"])
        self.assertIn("Hello there!", clean)
        self.assertIn("How are you?", clean)
    
    def test_inline_expressions(self):
        """Test expressions inline with text"""
        text = "Well *smirk* that's interesting *laugh*"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smirk", "laugh"])
        self.assertEqual(clean, "Well that's interesting")
    
    def test_invalid_expressions_filtered(self):
        """Test that invalid expressions are filtered out"""
        text = "*invalid* Hello *smile* world *unknown*"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smile"])
        self.assertEqual(clean, "Hello world")
    
    def test_empty_text(self):
        """Test parsing empty text"""
        expressions, clean = self.parser.parse("")
        
        self.assertEqual(expressions, [])
        self.assertEqual(clean, "")
    
    def test_no_expressions(self):
        """Test text with no expressions"""
        text = "Just plain text"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, [])
        self.assertEqual(clean, "Just plain text")
    
    def test_whitespace_normalization(self):
        """Test that whitespace is normalized"""
        text = "*smile*\n\n  Hello   \n  there!  \n*giggle*"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smile", "giggle"])
        self.assertEqual(clean, "Hello there!")
    
    def test_case_insensitive(self):
        """Test that expressions are case-insensitive"""
        text = "*SMILE* Hello *GiGgLe* there"
        expressions, clean = self.parser.parse(text)
        
        self.assertEqual(expressions, ["smile", "giggle"])
    
    def test_remove_expressions_method(self):
        """Test remove_expressions method"""
        text = "*smile* Hello *giggle* world"
        clean = self.parser.remove_expressions(text)
        
        self.assertEqual(clean, "Hello world")
    
    def test_extract_expressions_method(self):
        """Test extract_expressions method"""
        text = "*smile* Hello *giggle* world *invalid*"
        expressions = self.parser.extract_expressions(text)
        
        self.assertEqual(expressions, ["smile", "giggle"])
    
    def test_is_valid_expression(self):
        """Test is_valid_expression static method"""
        self.assertTrue(ExpressionParser.is_valid_expression("smile"))
        self.assertTrue(ExpressionParser.is_valid_expression("GIGGLE"))
        self.assertTrue(ExpressionParser.is_valid_expression("  blush  "))
        self.assertFalse(ExpressionParser.is_valid_expression("invalid"))
        self.assertFalse(ExpressionParser.is_valid_expression("notreal"))
    
    def test_all_supported_expressions(self):
        """Test that all supported expressions are recognized"""
        supported = ExpressionParser.SUPPORTED_EXPRESSIONS
        
        for expr in supported:
            text = f"*{expr}* text"
            expressions, _ = self.parser.parse(text)
            self.assertIn(expr, expressions)


if __name__ == "__main__":
    unittest.main()
