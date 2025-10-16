import os
from typing import Optional, Dict, Any, List
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
        "user_id": user_id,
        "source_url": source_url,
        "title": title,
        "raw_content": raw_content[:8000],
        "summary": summary[:8000],
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


