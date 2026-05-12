import os
from typing import Optional, Dict, Any, List

# Use local_storage for data persistence
from local_storage import local_storage


def upsert_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Upsert a user into local storage."""
    # Use a simple user_id derived from email
    user_id = email
    user = local_storage.get_user(user_id) or {"email": email}
    if name:
        user["name"] = name
    local_storage.save_user(user_id, user)
    return user


def insert_content(user_id: Optional[str], source_url: str, title: str, raw_content: str, summary: str) -> Dict[str, Any]:
    """Insert content into local JSON storage."""
    content_item = {
        "content_id": f"local_{int(__import__('time').time())}",
        "user_id": user_id,
        "source_url": source_url,
        "title": title,
        "raw_content": raw_content[:8000],
        "summary": summary[:8000],
        "created_at": __import__('time').strftime('%Y-%m-%dT%H:%M:%S')
    }

    # Save under a 'content' table in local_storage's sessions file to avoid adding new files
    local_storage.save_session(content_item["content_id"], content_item)
    return content_item


def get_recent_content(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve recent content items from local storage."""
    # Collect all sessions that look like content items
    # This is a simple best-effort fallback
    all_sessions = []
    try:
        # sessions are stored via local_storage.save_session
        import json
        if os.path.exists('sessions.json'):
            with open('sessions.json', 'r', encoding='utf-8') as f:
                sess = json.load(f)
                all_sessions = [v for k, v in sess.items() if isinstance(v, dict) and 'content_id' in v]
    except Exception:
        all_sessions = []

    # Sort by created_at if available
    def _created_at(item):
        return item.get('created_at', '')

    all_sessions.sort(key=_created_at, reverse=True)
    return all_sessions[:limit]


