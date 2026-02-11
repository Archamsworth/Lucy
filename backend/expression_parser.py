"""
Expression Parser for Lucy AI Companion
Extracts emotion tags from LLM responses and cleans text for TTS
"""

import re
from typing import List, Tuple


class ExpressionParser:
    """Parse and extract expression tags from model output"""
    
    # Supported expressions that map to animation triggers
    SUPPORTED_EXPRESSIONS = [
        "smile", "smirk", "pout", "giggle", "laugh", 
        "blush", "shy", "angry", "surprised", "thinking",
        "excited", "happy", "sad", "worried", "confused"
    ]
    
    def __init__(self):
        """Initialize expression parser"""
        self.expression_pattern = re.compile(r"\*(.*?)\*")
    
    def parse(self, text: str) -> Tuple[List[str], str]:
        """
        Extract expressions and clean text from model output
        
        Example input:
        *smile*
        Oh really? You think you can beat me?
        *giggle*
        That's cute.
        
        Returns: 
            Tuple of (expressions_list, clean_text)
            (['smile', 'giggle'], "Oh really? You think you can beat me? That's cute.")
        
        Args:
            text: Raw text from LLM with expression tags
            
        Returns:
            Tuple of (expressions list, clean text)
        """
        # Extract all expressions
        expressions = self.expression_pattern.findall(text)
        
        # Normalize expressions (lowercase and strip whitespace)
        expressions = [expr.lower().strip() for expr in expressions]
        
        # Filter to only supported expressions
        valid_expressions = [
            expr for expr in expressions 
            if expr in self.SUPPORTED_EXPRESSIONS
        ]
        
        # Remove expression tags from text
        clean_text = self.expression_pattern.sub("", text).strip()
        
        # Remove extra whitespace and normalize newlines
        clean_text = " ".join(clean_text.split())
        
        return valid_expressions, clean_text
    
    def remove_expressions(self, text: str) -> str:
        """
        Remove all expression tags from text
        
        Args:
            text: Text with expression tags
            
        Returns:
            Clean text without expression tags
        """
        clean_text = self.expression_pattern.sub("", text).strip()
        clean_text = " ".join(clean_text.split())
        return clean_text
    
    def extract_expressions(self, text: str) -> List[str]:
        """
        Extract only expressions from text
        
        Args:
            text: Text with expression tags
            
        Returns:
            List of valid expressions
        """
        expressions = self.expression_pattern.findall(text)
        expressions = [expr.lower().strip() for expr in expressions]
        return [expr for expr in expressions if expr in self.SUPPORTED_EXPRESSIONS]
    
    @staticmethod
    def is_valid_expression(expression: str) -> bool:
        """
        Check if an expression is valid/supported
        
        Args:
            expression: Expression string to validate
            
        Returns:
            True if expression is supported
        """
        return expression.lower().strip() in ExpressionParser.SUPPORTED_EXPRESSIONS


# Example usage and testing
if __name__ == "__main__":
    parser = ExpressionParser()
    
    # Test cases
    test_text1 = "*smile*\nHello there! How are you?\n*giggle*"
    expressions1, clean1 = parser.parse(test_text1)
    print(f"Test 1:")
    print(f"  Input: {test_text1!r}")
    print(f"  Expressions: {expressions1}")
    print(f"  Clean text: {clean1}")
    print()
    
    test_text2 = "*smirk* Oh really? *laugh* That's hilarious!"
    expressions2, clean2 = parser.parse(test_text2)
    print(f"Test 2:")
    print(f"  Input: {test_text2!r}")
    print(f"  Expressions: {expressions2}")
    print(f"  Clean text: {clean2}")
    print()
    
    # Test with invalid expressions
    test_text3 = "*invalid* Hello *smile* there *unknown*"
    expressions3, clean3 = parser.parse(test_text3)
    print(f"Test 3 (with invalid expressions):")
    print(f"  Input: {test_text3!r}")
    print(f"  Expressions: {expressions3}")
    print(f"  Clean text: {clean3}")
