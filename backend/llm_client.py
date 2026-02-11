"""
LLM Client for Lucy AI Companion
Connects to llama.cpp server for inference
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for LLM inference"""
    url: str = "http://localhost:8001/v1/chat/completions"
    temperature: float = 0.8
    top_p: float = 0.9
    max_tokens: int = 200
    repeat_penalty: float = 1.1
    timeout: int = 30


class LLMClient:
    """Client for interacting with llama.cpp server"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM client
        
        Args:
            config: LLM configuration (uses defaults if None)
        """
        self.config = config or LLMConfig()
    
    def generate(self, messages: List[Dict], 
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> str:
        """
        Generate completion from llama.cpp server
        
        Args:
            messages: List of message dicts with role and content
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated text response
            
        Raises:
            ConnectionError: If server is unreachable
            ValueError: If server returns error
        """
        # Use overrides or defaults
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # Prepare payload
        payload = {
            "messages": messages,
            "temperature": temp,
            "top_p": self.config.top_p,
            "max_tokens": max_tok,
            "repeat_penalty": self.config.repeat_penalty,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.config.url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"LLM server timeout after {self.config.timeout}s"
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to LLM server at {self.config.url}"
            )
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"LLM server error: {e.response.text}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid response format from LLM server: {e}")
    
    def check_health(self) -> bool:
        """
        Check if LLM server is healthy
        
        Returns:
            True if server is reachable and healthy
        """
        try:
            # Try to reach health endpoint
            base_url = self.config.url.rsplit('/', 2)[0]  # Get base URL
            response = requests.get(
                f"{base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Optional[Dict]:
        """
        Get model information from server
        
        Returns:
            Model info dict or None if unavailable
        """
        try:
            base_url = self.config.url.rsplit('/', 2)[0]
            response = requests.get(
                f"{base_url}/v1/models",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def update_config(self, **kwargs):
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = LLMClient()
    
    # Check health
    if not client.check_health():
        print("Warning: LLM server not reachable")
    else:
        print("LLM server is healthy")
    
    # Example generation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ]
    
    try:
        response = client.generate(messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
