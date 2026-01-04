"""
Conversation persistence - Save/load conversations as JSON.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import CONVERSATIONS_DIR
from models.conversation import Conversation, Message


def _generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Limit length
    return slug[:50].strip('-')


def _generate_session_id(name: str) -> str:
    """Generate a unique session ID from name."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = _generate_slug(name)
    return f"{date_str}_{slug}"


def create_conversation(name: Optional[str] = None) -> Conversation:
    """
    Create a new conversation.
    
    Args:
        name: Optional conversation name. If not provided, uses timestamp.
        
    Returns:
        New Conversation object
    """
    if not name:
        name = f"Conversation {datetime.now().strftime('%H:%M')}"
    
    session_id = _generate_session_id(name)
    now = datetime.now()
    
    return Conversation(
        session_id=session_id,
        name=name,
        created_at=now,
        updated_at=now,
        messages=[]
    )


def save_conversation(conversation: Conversation) -> Path:
    """
    Save conversation to JSON file.
    
    Returns:
        Path to saved file
    """
    file_path = CONVERSATIONS_DIR / f"{conversation.session_id}.json"
    
    # Convert to dict for JSON serialization
    data = conversation.model_dump(mode='json')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    return file_path


def load_conversation(session_id: str) -> Optional[Conversation]:
    """
    Load a conversation by session ID.
    
    Args:
        session_id: Full session ID or partial match
        
    Returns:
        Conversation object or None if not found
    """
    # Try exact match first
    file_path = CONVERSATIONS_DIR / f"{session_id}.json"
    if file_path.exists():
        return _load_from_file(file_path)
    
    # Try partial match
    for path in CONVERSATIONS_DIR.glob("*.json"):
        if session_id in path.stem:
            return _load_from_file(path)
    
    return None


def _load_from_file(file_path: Path) -> Optional[Conversation]:
    """Load conversation from file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Conversation(**data)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading conversation: {e}")
        return None


def list_conversations(limit: int = 20) -> list[dict]:
    """
    List recent conversations.
    
    Args:
        limit: Maximum number to return
        
    Returns:
        List of conversation summaries
    """
    conversations = []
    
    for path in sorted(CONVERSATIONS_DIR.glob("*.json"), reverse=True):
        if len(conversations) >= limit:
            break
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conversations.append({
                'session_id': data.get('session_id', path.stem),
                'name': data.get('name', 'Unnamed'),
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'message_count': len(data.get('messages', []))
            })
        except (json.JSONDecodeError, IOError):
            continue
    
    return conversations


def delete_conversation(session_id: str) -> bool:
    """
    Delete a conversation.
    
    Returns:
        True if deleted, False if not found
    """
    file_path = CONVERSATIONS_DIR / f"{session_id}.json"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def rename_conversation(session_id: str, new_name: str) -> Optional[Conversation]:
    """
    Rename a conversation.
    
    Note: This changes the name but keeps the session_id.
    """
    conv = load_conversation(session_id)
    if not conv:
        return None
    
    conv.name = new_name
    conv.updated_at = datetime.now()
    save_conversation(conv)
    return conv


def auto_generate_name(first_message: str) -> str:
    """
    Generate a conversation name from the first message.
    
    Examples:
        "Tell me about Reliance" -> "Analyzing Reliance"
        "Compare TCS vs Infosys" -> "Comparing TCS vs Infosys"
    """
    msg = first_message.lower().strip()
    
    # Common patterns
    if "compare" in msg:
        return first_message.title()[:50]
    
    if "tell me about" in msg:
        topic = msg.replace("tell me about", "").strip()
        return f"Analyzing {topic.title()}"[:50]
    
    if "analyze" in msg or "analysis" in msg:
        return first_message.title()[:50]
    
    if "what" in msg and "?" in msg:
        return first_message[:40]
    
    # Default: Extract key topic
    words = first_message.split()
    if len(words) <= 3:
        return first_message.title()
    
    # For longer messages, take first few meaningful words
    return " ".join(words[:5]).title()[:50]
