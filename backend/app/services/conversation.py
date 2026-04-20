"""Conversation session management for multi-turn chat"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class ConversationManager:
    """Manages chat sessions and conversation history"""

    def __init__(self):
        """Initialize conversation manager with empty sessions"""
        self.sessions: Dict[str, Dict] = {}

    def create_session(self, system_prompt: Optional[str] = None) -> str:
        """
        Create a new conversation session.

        Args:
            system_prompt: Optional system message to initialize conversation

        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        self.sessions[session_id] = {
            "messages": messages,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return session_id

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to a conversation session.

        Args:
            session_id: The session ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content text

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id]["messages"].append({"role": role, "content": content})
        self.sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get all messages from a conversation session.

        Args:
            session_id: The session ID

        Returns:
            List of message dicts with 'role' and 'content'

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        return self.sessions[session_id]["messages"]

    def delete_session(self, session_id: str) -> None:
        """
        Delete a conversation session.

        Args:
            session_id: The session ID

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        del self.sessions[session_id]

    def get_session_info(self, session_id: str) -> Dict:
        """
        Get metadata about a session (timestamps, message count).

        Args:
            session_id: The session ID

        Returns:
            Dict with 'created_at', 'updated_at', 'message_count'

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        return {
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "message_count": len(session["messages"]),
        }
