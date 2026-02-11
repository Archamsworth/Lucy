"""
Conversation Manager for Lucy AI Companion
Handles conversation history and context management
"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationManager:
    """Manage conversation history for multiple users"""
    
    def __init__(self, max_history: int = 6):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of exchanges to keep (default: 6)
        """
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict]] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def get_history(self, user_id: str) -> List[Dict]:
        """
        Get conversation history for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of message dictionaries with role and content
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.metadata[user_id] = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
        return self.conversations[user_id]
    
    def add_message(self, user_id: str, role: str, content: str):
        """
        Add a message to conversation history
        
        Args:
            user_id: User identifier
            role: Message role ("user" or "assistant")
            content: Message content
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.metadata[user_id] = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
        
        # Add message
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        # Update metadata
        self.metadata[user_id]["message_count"] += 1
        self.metadata[user_id]["last_updated"] = datetime.now().isoformat()
        
        # Trim history if needed (keep last N exchanges = 2N messages)
        max_messages = self.max_history * 2
        if len(self.conversations[user_id]) > max_messages:
            self.conversations[user_id] = self.conversations[user_id][-max_messages:]
    
    def clear_history(self, user_id: str):
        """
        Clear conversation history for a user
        
        Args:
            user_id: User identifier
        """
        if user_id in self.conversations:
            self.conversations[user_id] = []
            self.metadata[user_id]["cleared_at"] = datetime.now().isoformat()
            self.metadata[user_id]["message_count"] = 0
    
    def get_metadata(self, user_id: str) -> Optional[Dict]:
        """
        Get metadata for a user's conversation
        
        Args:
            user_id: User identifier
            
        Returns:
            Metadata dictionary or None
        """
        return self.metadata.get(user_id)
    
    def format_for_llm(self, user_id: str, system_prompt: str, 
                       new_message: str) -> List[Dict]:
        """
        Format conversation history for LLM input
        
        Args:
            user_id: User identifier
            system_prompt: System prompt to prepend
            new_message: New user message to append
            
        Returns:
            Complete message list ready for LLM
        """
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.get_history(user_id))
        messages.append({"role": "user", "content": new_message})
        return messages
    
    def get_exchange_count(self, user_id: str) -> int:
        """
        Get number of exchanges (user+assistant pairs) in history
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of exchanges
        """
        history = self.get_history(user_id)
        return len(history) // 2
    
    def export_history(self, user_id: str) -> Dict:
        """
        Export full conversation data for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with history and metadata
        """
        return {
            "user_id": user_id,
            "history": self.get_history(user_id),
            "metadata": self.get_metadata(user_id),
            "exchange_count": self.get_exchange_count(user_id)
        }
    
    def list_users(self) -> List[str]:
        """
        Get list of all user IDs with conversation history
        
        Returns:
            List of user IDs
        """
        return list(self.conversations.keys())


# Example usage
if __name__ == "__main__":
    manager = ConversationManager(max_history=3)
    
    # Simulate conversation
    user_id = "test_user"
    
    manager.add_message(user_id, "user", "Hello!")
    manager.add_message(user_id, "assistant", "*smile* Hi there!")
    
    manager.add_message(user_id, "user", "How are you?")
    manager.add_message(user_id, "assistant", "*happy* I'm great, thanks!")
    
    # Get history
    history = manager.get_history(user_id)
    print(f"History: {history}")
    print(f"Exchange count: {manager.get_exchange_count(user_id)}")
    print(f"Metadata: {manager.get_metadata(user_id)}")
    
    # Format for LLM
    messages = manager.format_for_llm(
        user_id, 
        "You are a helpful assistant", 
        "Tell me a joke"
    )
    print(f"\nFormatted for LLM: {messages}")
