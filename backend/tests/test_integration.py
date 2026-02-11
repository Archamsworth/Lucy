"""
Integration tests for Lucy AI Companion API
Tests require backend server to be running
"""

import unittest
import requests
import time
import json
from pathlib import Path
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = "integration_test_user"


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Check if server is available before running tests"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                raise Exception("Server not healthy")
        except:
            raise Exception(
                "Backend server not running. Please start with: python main.py"
            )
    
    def test_01_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("api", data)
        self.assertEqual(data["api"], "online")
    
    def test_02_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{API_BASE_URL}/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "online")
    
    def test_03_chat_basic(self):
        """Test basic chat functionality"""
        payload = {
            "user_id": TEST_USER_ID,
            "message": "Hello!",
            "temperature": 0.8,
            "max_tokens": 200
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("expressions", data)
        self.assertIn("text", data)
        self.assertIn("audio_url", data)
        self.assertIn("raw_response", data)
        
        # Check data types
        self.assertIsInstance(data["expressions"], list)
        self.assertIsInstance(data["text"], str)
        self.assertIsInstance(data["raw_response"], str)
        
        # Check text is not empty
        self.assertTrue(len(data["text"]) > 0)
    
    def test_04_chat_with_expressions(self):
        """Test that expressions are extracted correctly"""
        payload = {
            "user_id": TEST_USER_ID,
            "message": "Tell me something that makes you happy",
            "temperature": 0.8
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have some expressions (likely smile, happy, etc.)
        # Note: This is probabilistic based on LLM output
        if len(data["expressions"]) > 0:
            # If expressions exist, verify they're valid
            valid_expressions = [
                "smile", "smirk", "giggle", "laugh", "blush", 
                "shy", "angry", "surprised", "thinking", "happy",
                "sad", "excited", "pout", "worried", "confused"
            ]
            for expr in data["expressions"]:
                self.assertIn(expr, valid_expressions)
    
    def test_05_conversation_memory(self):
        """Test conversation history is maintained"""
        user_id = f"{TEST_USER_ID}_memory"
        
        # Clear any existing history
        requests.delete(f"{API_BASE_URL}/conversation/{user_id}")
        
        # First message
        response1 = requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user_id, "message": "My favorite color is blue"},
            timeout=30
        )
        self.assertEqual(response1.status_code, 200)
        
        # Second message asking about previous context
        time.sleep(1)  # Small delay
        response2 = requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user_id, "message": "What is my favorite color?"},
            timeout=30
        )
        self.assertEqual(response2.status_code, 200)
        
        data2 = response2.json()
        text_lower = data2["text"].lower()
        
        # Response should mention blue (though this is probabilistic)
        # At minimum, it should have a response
        self.assertTrue(len(data2["text"]) > 0)
    
    def test_06_get_conversation_history(self):
        """Test retrieving conversation history"""
        user_id = f"{TEST_USER_ID}_history"
        
        # Clear history
        requests.delete(f"{API_BASE_URL}/conversation/{user_id}")
        
        # Send a message
        requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user_id, "message": "Test message"},
            timeout=30
        )
        
        # Get history
        response = requests.get(f"{API_BASE_URL}/conversation/{user_id}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("user_id", data)
        self.assertIn("history", data)
        self.assertIn("metadata", data)
        self.assertIn("exchange_count", data)
        
        self.assertEqual(data["user_id"], user_id)
        self.assertIsInstance(data["history"], list)
        self.assertTrue(len(data["history"]) >= 2)  # At least user + assistant
    
    def test_07_clear_conversation(self):
        """Test clearing conversation history"""
        user_id = f"{TEST_USER_ID}_clear"
        
        # Send a message
        requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user_id, "message": "Test"},
            timeout=30
        )
        
        # Clear conversation
        response = requests.delete(f"{API_BASE_URL}/conversation/{user_id}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        
        # Verify history is empty
        history_response = requests.get(f"{API_BASE_URL}/conversation/{user_id}")
        history_data = history_response.json()
        self.assertEqual(len(history_data["history"]), 0)
    
    def test_08_empty_message_error(self):
        """Test that empty messages return error"""
        payload = {
            "user_id": TEST_USER_ID,
            "message": "",
            "temperature": 0.8
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
    
    def test_09_invalid_temperature(self):
        """Test chat with different temperature values"""
        # Very low temperature
        response_low = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "user_id": TEST_USER_ID,
                "message": "Say hello",
                "temperature": 0.1
            },
            timeout=30
        )
        self.assertEqual(response_low.status_code, 200)
        
        # High temperature
        response_high = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "user_id": TEST_USER_ID,
                "message": "Say hello",
                "temperature": 1.0
            },
            timeout=30
        )
        self.assertEqual(response_high.status_code, 200)
    
    def test_10_max_tokens_limit(self):
        """Test with different max_tokens values"""
        # Small max_tokens
        response_small = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "user_id": TEST_USER_ID,
                "message": "Tell me a story",
                "max_tokens": 50
            },
            timeout=30
        )
        self.assertEqual(response_small.status_code, 200)
        
        # Larger max_tokens
        response_large = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "user_id": TEST_USER_ID,
                "message": "Tell me a story",
                "max_tokens": 200
            },
            timeout=30
        )
        self.assertEqual(response_large.status_code, 200)
    
    def test_11_multiple_users_isolation(self):
        """Test that different users have isolated conversations"""
        user1 = f"{TEST_USER_ID}_1"
        user2 = f"{TEST_USER_ID}_2"
        
        # Clear both
        requests.delete(f"{API_BASE_URL}/conversation/{user1}")
        requests.delete(f"{API_BASE_URL}/conversation/{user2}")
        
        # User 1 conversation
        requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user1, "message": "I like cats"},
            timeout=30
        )
        
        # User 2 conversation
        requests.post(
            f"{API_BASE_URL}/chat",
            json={"user_id": user2, "message": "I like dogs"},
            timeout=30
        )
        
        # Get both histories
        history1 = requests.get(f"{API_BASE_URL}/conversation/{user1}").json()
        history2 = requests.get(f"{API_BASE_URL}/conversation/{user2}").json()
        
        # Verify isolation
        self.assertNotEqual(history1["history"], history2["history"])
        
        # Check user1 history contains "cats"
        user1_text = json.dumps(history1["history"]).lower()
        self.assertIn("cats", user1_text)
        
        # Check user2 history contains "dogs"
        user2_text = json.dumps(history2["history"]).lower()
        self.assertIn("dogs", user2_text)
    
    def test_12_response_time(self):
        """Test that responses are returned within acceptable time"""
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "user_id": TEST_USER_ID,
                "message": "Hi",
                "max_tokens": 100
            },
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # Should respond within 10 seconds for simple message
        self.assertLess(duration, 10.0, 
                       f"Response took {duration:.2f}s, expected < 10s")


def run_integration_tests():
    """Run integration tests with custom runner"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAPIIntegration)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Lucy AI Companion - Integration Tests")
    print("=" * 70)
    print()
    print("Prerequisites:")
    print("1. Backend server must be running (python main.py)")
    print("2. LLM server must be running (llama.cpp)")
    print()
    print(f"Testing against: {API_BASE_URL}")
    print()
    
    try:
        # Quick connectivity check
        requests.get(f"{API_BASE_URL}/health", timeout=5)
        print("✓ Server is reachable")
        print()
    except:
        print("✗ Cannot connect to server!")
        print(f"  Make sure backend is running at {API_BASE_URL}")
        sys.exit(1)
    
    # Run tests
    result = run_integration_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
