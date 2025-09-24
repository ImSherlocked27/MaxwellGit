import os
import json
import time
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class ChatManager:
    """
    Comprehensive chat management system that handles:
    - Creating new chats
    - Listing existing chats 
    - Loading and saving chat messages
    - Deleting chats
    - Renaming chats
    - Auto-generating chat titles from first message
    """
    
    def __init__(self, base_dir: str = "./chat_histories"):
        self.base_dir = base_dir
        self._ensure_base_dir()
    
    def _ensure_base_dir(self) -> None:
        """Ensure the base chat directory exists"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for safe filesystem usage"""
        import re
        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        sanitized = re.sub(r'[^\w\s\-_.]', '_', sanitized)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:100]  # Limit length
    
    def _get_user_collection_dir(self, user_id: str, collection_name: str) -> str:
        """Get the directory path for a specific user and collection"""
        user_safe = self._sanitize_filename(user_id or "anonymous")
        collection_safe = self._sanitize_filename(collection_name or "default")
        dir_path = os.path.join(self.base_dir, f"{user_safe}__{collection_safe}")
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        return dir_path
    
    def _get_chat_file_path(self, user_id: str, collection_name: str, chat_id: str) -> str:
        """Get the file path for a specific chat"""
        dir_path = self._get_user_collection_dir(user_id, collection_name)
        filename = f"{self._sanitize_filename(chat_id)}.json"
        return os.path.join(dir_path, filename)
    
    def _generate_chat_title(self, messages: List[Dict]) -> str:
        """Generate a chat title from the first user message"""
        for message in messages:
            if message.get("role") == "user" and message.get("content"):
                content = message["content"].strip()
                if content:
                    # Take first 50 characters and add ellipsis if longer
                    title = content[:50]
                    if len(content) > 50:
                        title += "..."
                    return title
        
        # Fallback to timestamp if no user message found
        return f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    def create_chat(self, user_id: str, collection_name: str, title: Optional[str] = None) -> str:
        """
        Create a new chat and return its ID
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            title: Optional custom title (will be auto-generated if None)
        
        Returns:
            str: The new chat ID
        """
        chat_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        chat_data = {
            "chat_id": chat_id,
            "title": title or f"New Chat",
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": [],
            "user_id": user_id,
            "collection_name": collection_name
        }
        
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            return chat_id
        except Exception as e:
            raise RuntimeError(f"Failed to create chat: {e}")
    
    def list_chats(self, user_id: str, collection_name: str) -> List[Dict]:
        """
        List all chats for a user and collection, sorted by most recent first
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
        
        Returns:
            List[Dict]: List of chat metadata dictionaries
        """
        dir_path = self._get_user_collection_dir(user_id, collection_name)
        chats = []
        
        try:
            if not os.path.exists(dir_path):
                return []
            
            for filename in os.listdir(dir_path):
                if not filename.endswith(".json"):
                    continue
                
                file_path = os.path.join(dir_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        chat_data = json.load(f)
                    
                    if isinstance(chat_data, dict) and "chat_id" in chat_data:
                        chats.append({
                            "chat_id": chat_data["chat_id"],
                            "title": chat_data.get("title", "Untitled Chat"),
                            "created_at": chat_data.get("created_at", ""),
                            "updated_at": chat_data.get("updated_at", ""),
                            "message_count": len(chat_data.get("messages", []))
                        })
                except Exception:
                    # Skip corrupted files
                    continue
            
            # Sort by updated_at descending (most recent first)
            chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return chats
            
        except Exception:
            return []
    
    def load_chat_messages(self, user_id: str, collection_name: str, chat_id: str) -> List[Dict]:
        """
        Load messages for a specific chat
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
        
        Returns:
            List[Dict]: List of message dictionaries
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            return chat_data.get("messages", [])
            
        except Exception:
            return []
    
    def _serialize_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Serialize messages to ensure they are JSON-compatible
        
        Args:
            messages: List of message dictionaries that may contain non-serializable objects
            
        Returns:
            List[Dict]: Serialized messages safe for JSON storage
        """
        serialized_messages = []
        
        for message in messages:
            serialized_message = message.copy()
            
            # Handle documents field if present
            if "documents" in serialized_message:
                serializable_docs = []
                for doc in serialized_message["documents"]:
                    if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                        # LangChain Document object
                        serializable_docs.append({
                            "page_content": doc.page_content,
                            "metadata": doc.metadata
                        })
                    elif isinstance(doc, dict):
                        # Already a dictionary
                        serializable_docs.append(doc)
                    else:
                        # Fallback: convert to string
                        serializable_docs.append({
                            "page_content": str(doc),
                            "metadata": {}
                        })
                serialized_message["documents"] = serializable_docs
            
            serialized_messages.append(serialized_message)
        
        return serialized_messages
    
    def save_chat_messages(self, user_id: str, collection_name: str, chat_id: str, messages: List[Dict]) -> None:
        """
        Save messages for a specific chat
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
            messages: List of message dictionaries to save
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Load existing chat data or create new
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
            else:
                chat_data = {
                    "chat_id": chat_id,
                    "title": "New Chat",
                    "created_at": timestamp,
                    "user_id": user_id,
                    "collection_name": collection_name
                }
            
            # Serialize messages to ensure JSON compatibility
            serialized_messages = self._serialize_messages(messages or [])
            
            # Update messages and timestamp
            chat_data["messages"] = serialized_messages
            chat_data["updated_at"] = timestamp
            
            # Auto-generate title from first message if title is still default
            if chat_data.get("title") in ["New Chat", f"New Chat"] and serialized_messages:
                chat_data["title"] = self._generate_chat_title(serialized_messages)
            
            # Save back to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise RuntimeError(f"Failed to save chat messages: {e}")
    
    def delete_chat(self, user_id: str, collection_name: str, chat_id: str) -> bool:
        """
        Delete a specific chat
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def rename_chat(self, user_id: str, collection_name: str, chat_id: str, new_title: str) -> bool:
        """
        Rename a specific chat
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
            new_title: New title for the chat
        
        Returns:
            bool: True if rename was successful, False otherwise
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            chat_data["title"] = new_title.strip() or "Untitled Chat"
            chat_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def get_chat_info(self, user_id: str, collection_name: str, chat_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific chat
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
        
        Returns:
            Optional[Dict]: Chat information or None if not found
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            return {
                "chat_id": chat_data.get("chat_id"),
                "title": chat_data.get("title", "Untitled Chat"),
                "created_at": chat_data.get("created_at", ""),
                "updated_at": chat_data.get("updated_at", ""),
                "message_count": len(chat_data.get("messages", [])),
                "user_id": chat_data.get("user_id"),
                "collection_name": chat_data.get("collection_name")
            }
            
        except Exception:
            return None
    
    def clear_chat_messages(self, user_id: str, collection_name: str, chat_id: str) -> bool:
        """
        Clear all messages from a chat but keep the chat itself
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.save_chat_messages(user_id, collection_name, chat_id, [])
            return True
        except Exception:
            return False
    
    def export_chat(self, user_id: str, collection_name: str, chat_id: str) -> Optional[Dict]:
        """
        Export a complete chat for backup or transfer
        
        Args:
            user_id: User identifier
            collection_name: Collection/database name
            chat_id: Chat identifier
        
        Returns:
            Optional[Dict]: Complete chat data or None if not found
        """
        file_path = self._get_chat_file_path(user_id, collection_name, chat_id)
        
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except Exception:
            return None
    
    def import_chat(self, chat_data: Dict) -> Optional[str]:
        """
        Import a chat from exported data
        
        Args:
            chat_data: Complete chat data dictionary
        
        Returns:
            Optional[str]: New chat ID if successful, None otherwise
        """
        try:
            user_id = chat_data.get("user_id")
            collection_name = chat_data.get("collection_name")
            
            if not user_id or not collection_name:
                return None
            
            # Generate new chat ID to avoid conflicts
            new_chat_id = str(uuid.uuid4())
            chat_data["chat_id"] = new_chat_id
            
            file_path = self._get_chat_file_path(user_id, collection_name, new_chat_id)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            return new_chat_id
            
        except Exception:
            return None


# Global instance for easy usage
chat_manager = ChatManager()

# Legacy compatibility functions (for existing code)
def create_chat(user_id: str, collection_name: str, title: Optional[str] = None) -> str:
    """Legacy compatibility wrapper"""
    return chat_manager.create_chat(user_id, collection_name, title)

def list_chats(user_id: str, collection_name: str) -> List[Dict]:
    """Legacy compatibility wrapper"""
    return chat_manager.list_chats(user_id, collection_name)

def load_chat_messages(user_id: str, collection_name: str, chat_id: str) -> List[Dict]:
    """Legacy compatibility wrapper"""
    return chat_manager.load_chat_messages(user_id, collection_name, chat_id)

def save_chat_messages(user_id: str, collection_name: str, chat_id: str, messages: List[Dict]) -> None:
    """Legacy compatibility wrapper"""
    chat_manager.save_chat_messages(user_id, collection_name, chat_id, messages)

def delete_chat_by_id(user_id: str, collection_name: str, chat_id: str) -> None:
    """Legacy compatibility wrapper"""
    chat_manager.delete_chat(user_id, collection_name, chat_id)

def rename_chat(user_id: str, collection_name: str, chat_id: str, new_title: str) -> None:
    """Legacy compatibility wrapper"""
    chat_manager.rename_chat(user_id, collection_name, chat_id, new_title) 