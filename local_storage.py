"""
Local storage system for data persistence
Provides basic user data and source management using JSON files
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class LocalStorage:
    """Simple local storage system using JSON files"""
    
    def __init__(self):
        self.users_file = "users.json"
        self.sources_file = "sources.json"
        self.sessions_file = "sessions.json"
    
    def _load_json(self, filename: str, default: Any = None) -> Any:
        """Load data from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return default if default is not None else {}
    
    def _save_json(self, filename: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data by ID"""
        users = self._load_json(self.users_file, {})
        return users.get(user_id)
    
    def save_user(self, user_id: str, user_data: Dict) -> bool:
        """Save user data"""
        users = self._load_json(self.users_file, {})
        users[user_id] = user_data
        return self._save_json(self.users_file, users)
    
    def get_user_sources(self, user_id: str) -> List[Dict]:
        """Get sources for a user"""
        sources = self._load_json(self.sources_file, {})
        return sources.get(user_id, [])
    
    def save_user_sources(self, user_id: str, sources: List[Dict]) -> bool:
        """Save sources for a user"""
        all_sources = self._load_json(self.sources_file, {})
        all_sources[user_id] = sources
        return self._save_json(self.sources_file, all_sources)
    
    def add_source(self, user_id: str, source: Dict) -> bool:
        """Add a source for a user"""
        sources = self.get_user_sources(user_id)
        source['id'] = len(sources) + 1  # Simple ID generation
        source['added_at'] = datetime.now().isoformat()
        sources.append(source)
        return self.save_user_sources(user_id, sources)
    
    def delete_source(self, user_id: str, source_id: int) -> bool:
        """Delete a source for a user"""
        sources = self.get_user_sources(user_id)
        sources = [s for s in sources if s.get('id') != source_id]
        return self.save_user_sources(user_id, sources)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        sessions = self._load_json(self.sessions_file, {})
        return sessions.get(session_id)
    
    def save_session(self, session_id: str, session_data: Dict) -> bool:
        """Save session data"""
        sessions = self._load_json(self.sessions_file, {})
        sessions[session_id] = session_data
        return self._save_json(self.sessions_file, sessions)

# Global instance
local_storage = LocalStorage()
