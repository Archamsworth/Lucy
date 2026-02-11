"""
Unit tests for Conversation Manager
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_manager import ConversationManager


class TestConversationManager(unittest.TestCase):
    """Test cases for ConversationManager"""
    
    def setUp(self):
        """Set up test manager"""
        self.manager = ConversationManager(max_history=3)
    
    def test_new_user_empty_history(self):
        """Test that new user has empty history"""
        history = self.manager.get_history("new_user")
        self.assertEqual(history, [])
    
    def test_add_message(self):
        """Test adding messages to history"""
        user_id = "test_user"
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi there!")
        
        history = self.manager.get_history(user_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["role"], "assistant")
    
    def test_history_trimming(self):
        """Test that history is trimmed to max_history exchanges"""
        user_id = "test_user"
        
        # Add 5 exchanges (10 messages)
        for i in range(5):
            self.manager.add_message(user_id, "user", f"Message {i}")
            self.manager.add_message(user_id, "assistant", f"Response {i}")
        
        history = self.manager.get_history(user_id)
        
        # Should only keep last 3 exchanges (6 messages)
        self.assertEqual(len(history), 6)
        # Should start from exchange 2
        self.assertEqual(history[0]["content"], "Message 2")
    
    def test_clear_history(self):
        """Test clearing conversation history"""
        user_id = "test_user"
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi")
        
        self.manager.clear_history(user_id)
        history = self.manager.get_history(user_id)
        
        self.assertEqual(len(history), 0)
    
    def test_metadata_tracking(self):
        """Test that metadata is tracked correctly"""
        user_id = "test_user"
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi")
        
        metadata = self.manager.get_metadata(user_id)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["message_count"], 2)
        self.assertIn("created_at", metadata)
        self.assertIn("last_updated", metadata)
    
    def test_format_for_llm(self):
        """Test formatting messages for LLM"""
        user_id = "test_user"
        system_prompt = "You are a helpful assistant"
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi there!")
        
        messages = self.manager.format_for_llm(
            user_id, system_prompt, "How are you?"
        )
        
        # Should have system + history + new message
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], system_prompt)
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"], "How are you?")
    
    def test_exchange_count(self):
        """Test exchange counting"""
        user_id = "test_user"
        
        self.assertEqual(self.manager.get_exchange_count(user_id), 0)
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi")
        
        self.assertEqual(self.manager.get_exchange_count(user_id), 1)
        
        self.manager.add_message(user_id, "user", "How are you?")
        self.manager.add_message(user_id, "assistant", "Good!")
        
        self.assertEqual(self.manager.get_exchange_count(user_id), 2)
    
    def test_export_history(self):
        """Test exporting conversation data"""
        user_id = "test_user"
        
        self.manager.add_message(user_id, "user", "Hello")
        self.manager.add_message(user_id, "assistant", "Hi")
        
        export = self.manager.export_history(user_id)
        
        self.assertEqual(export["user_id"], user_id)
        self.assertEqual(len(export["history"]), 2)
        self.assertEqual(export["exchange_count"], 1)
        self.assertIn("metadata", export)
    
    def test_list_users(self):
        """Test listing all users"""
        self.manager.add_message("user1", "user", "Hello")
        self.manager.add_message("user2", "user", "Hi")
        self.manager.add_message("user3", "user", "Hey")
        
        users = self.manager.list_users()
        
        self.assertEqual(len(users), 3)
        self.assertIn("user1", users)
        self.assertIn("user2", users)
        self.assertIn("user3", users)
    
    def test_multiple_users_isolated(self):
        """Test that different users have isolated histories"""
        self.manager.add_message("user1", "user", "Message 1")
        self.manager.add_message("user2", "user", "Message 2")
        
        history1 = self.manager.get_history("user1")
        history2 = self.manager.get_history("user2")
        
        self.assertEqual(len(history1), 1)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history1[0]["content"], "Message 1")
        self.assertEqual(history2[0]["content"], "Message 2")


if __name__ == "__main__":
    unittest.main()
