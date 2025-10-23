import os
from typing import Optional, Dict, Any, List
<<<<<<< HEAD

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
=======
from dotenv import load_dotenv

load_dotenv()

_supabase: Optional[object] = None

def get_client():
    global _supabase
    if _supabase is None:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        if not url or not key:
            raise RuntimeError('SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env')
        try:
            from supabase import create_client  # lazy import to avoid startup crash if not installed
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError("Supabase client not installed. Run: pip install -r requirements.txt") from e
        _supabase = create_client(url, key)
    return _supabase

def upsert_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    sb = get_client()
    payload = {"email": email}
    if name:
        payload["name"] = name
    
    try:
        # Use upsert with on_conflict parameter
        resp = sb.table('users').upsert(payload, on_conflict='email').execute()
        return resp.data[0] if resp.data else payload
    except Exception as e:
        print(f"Error in upsert_user: {e}")
        # Fallback: try insert
        try:
            resp = sb.table('users').insert(payload).execute()
            return resp.data[0] if resp.data else payload
        except Exception as e2:
            print(f"Insert also failed: {e2}")
            return payload

def insert_content(user_id: Optional[str], source_url: str, title: str, raw_content: str, summary: str) -> Dict[str, Any]:
    sb = get_client()
    payload = {
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
        "user_id": user_id,
        "source_url": source_url,
        "title": title,
        "raw_content": raw_content[:8000],
        "summary": summary[:8000],
<<<<<<< HEAD
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
=======
    }
    try:
        resp = sb.table('content').insert(payload).execute()
        return resp.data[0] if resp.data else payload
    except Exception as e:
        print(f"Error in insert_content: {e}")
        return payload

def get_recent_content(limit: int = 20) -> List[Dict[str, Any]]:
    sb = get_client()
    resp = sb.table('content').select('*').order('created_at', desc=True).limit(limit).execute()
    return resp.data or []
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15


