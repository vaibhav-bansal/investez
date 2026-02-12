"""
Conversation models for persistence.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    """Single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    agent: Optional[str] = None  # Which agent handled this (for assistant messages)
    tools_used: Optional[list[str]] = None  # Tools called for this response


class Conversation(BaseModel):
    """A full conversation session."""
    session_id: str  # Format: YYYY-MM-DD_slug
    name: str  # Human-readable name
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = []
    
    def add_user_message(self, content: str) -> Message:
        """Add a user message to the conversation."""
        msg = Message(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg
    
    def add_assistant_message(
        self,
        content: str,
        agent: Optional[str] = None,
        tools_used: Optional[list[str]] = None
    ) -> Message:
        """Add an assistant message to the conversation."""
        msg = Message(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            agent=agent,
            tools_used=tools_used
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg
    
    def get_context(self, max_messages: int = 10) -> list[dict]:
        """Get recent messages formatted for Claude API."""
        recent = self.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]
    
    def get_last_user_query(self) -> Optional[str]:
        """Get the most recent user message content."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None
    
    def get_summary(self) -> str:
        """Get a brief summary of the conversation."""
        if not self.messages:
            return "Empty conversation"
        
        user_msgs = [m for m in self.messages if m.role == "user"]
        if user_msgs:
            first_query = user_msgs[0].content[:50]
            return f"{first_query}... ({len(self.messages)} messages)"
        return f"{len(self.messages)} messages"
