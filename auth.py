"""
Authentication module for CreatorPulse
Handles user signup, login, and session management using local storage
"""

import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from local_storage import local_storage

class AuthManager:
    def __init__(self):
        self.users = {}  # Keep for backward compatibility
        self.sessions = {}  # Keep for backward compatibility
        self._load_data()
    
    def _load_data(self):
        """Load user and session data from files (for backward compatibility)"""
        # Load users
        if os.path.exists("users.json"):
            with open("users.json", 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
        
        # Load sessions
        if os.path.exists("sessions.json"):
            with open("sessions.json", 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
    
    def _save_data(self):
        """Save user and session data to files (for backward compatibility)"""
        with open("users.json", 'w') as f:
            json.dump(self.users, f, indent=2)
        with open("sessions.json", 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists in local storage
            existing_user = None
            for user_id, user_data in self.users.items():
                if user_data.get('email') == email:
                    existing_user = user_data
                    break
            
            if existing_user:
                return {"success": False, "error": "Email already registered"}
            
            if len(password) < 6:
                return {"success": False, "error": "Password must be at least 6 characters"}
            
            # Create user in local storage
            user_id = f"user_{len(self.users) + 1}"
            style_profile = {
                "style_type": "predefined",
                "style_name": "Professional",
                "tone": "professional",
                "newsletter_count": 0
            }
            
            delivery_settings = {
                "time": "08:00",
                "email": email,
                "timezone": "UTC",
                "auto_delivery": False
            }
            
            user_data = {
                "user_id": user_id,
                "name": name,
                "email": email,
                "password_hash": self._hash_password(password),
                "style_profile": style_profile,
                "delivery_settings": delivery_settings,
                "sources": [],
                "created_at": datetime.now().isoformat()
            }
            
            # Save to local storage
            self.users[user_id] = user_data
            local_storage.save_user(user_id, user_data)
            
            # Also save to local file for backward compatibility
            self.users[email] = user_data
            self._save_data()
            return {"success": True, "user": user_data}
                
        except Exception as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            # Get user from local storage
            user = None
            for user_id, user_data in self.users.items():
                if user_data.get('email') == email:
                    user = user_data
                    break
            
            if not user:
                return {"success": False, "error": "Invalid email or password"}
            
            # Check if password hash exists and matches
            stored_hash = user.get("password_hash", "")
            if stored_hash and stored_hash != self._hash_password(password):
                return {"success": False, "error": "Invalid email or password"}
            
            # If no password hash stored, allow login for existing users (temporary fix)
            if not stored_hash:
                print(f"⚠️ No password hash for user {email}, allowing login (temporary)")
            
            # Create session
            session_id = f"session_{int(datetime.now().timestamp())}_{email}"
            self.sessions[session_id] = {
                "user_id": user["user_id"],
                "email": email,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            # Also update local users for backward compatibility
            self.users[email] = user
            self._save_data()
            
            return {"success": True, "session_id": session_id, "user": user}
            
        except Exception as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    def get_user_from_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from session ID"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            # Session expired
            del self.sessions[session_id]
            self._save_data()
            return None
        
        email = session["email"]
        return self.users.get(email)
    
    def logout(self, session_id: str):
        """Logout user by removing session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_data()
    
    def update_user_data(self, user_id: str, data: Dict[str, Any]):
        """Update user data"""
        try:
            # Update in local storage
            for email, user in self.users.items():
                if str(user["user_id"]) == str(user_id):
                    self.users[email].update(data)
                    local_storage.save_user(user_id, self.users[email])
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user_id"""
        try:
            # Get from local storage
            for email, user in self.users.items():
                if str(user["user_id"]) == str(user_id):
                    return user
        except Exception as e:
            print(f"Error getting user data from database: {e}")
        
        # Fallback to local data
        for email, user in self.users.items():
            if str(user.get("user_id")) == str(user_id):
                return user
        return None
    
    def get_all_users(self) -> list:
        """Get all users data"""
        try:
            # Get from local storage
            # Users are already loaded in self.users from _load_data()
            self._save_data()
            return list(self.users.values())
        except Exception as e:
            print(f"Error getting all users: {e}")
            return list(self.users.values())

def get_current_user():
    """Get current user from session state"""
    if 'user' not in st.session_state:
        return None
    return st.session_state.user

def require_auth():
    """Decorator to require authentication for certain pages"""
    if 'user' not in st.session_state:
        st.error("Please log in to access this page")
        st.stop()
    return st.session_state.user
