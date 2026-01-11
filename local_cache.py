"""Simple caching system with TTL for content freshness."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class LocalCache:
    def __init__(self, cache_file: str = "content_cache.json", ttl_minutes: int = 30):
        """Initialize the local cache with TTL support.
        
        Args:
            cache_file: Path to the cache file
            ttl_minutes: Time-to-live in minutes for cached content
        """
        self.cache_file = cache_file
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load the cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """Save the cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from cache if it exists and is not expired.
        
        Args:
            key: Cache key (typically a URL)
            
        Returns:
            Cached content if valid, None if expired or missing
        """
        if key in self.cache:
            item = self.cache[key]
            cached_time = datetime.fromisoformat(item['cached_at'])
            
            # Check if cached content is still valid
            if datetime.now() - cached_time <= self.ttl:
                return item['content']
            else:
                # Remove expired content
                logger.info(f"Cache expired for {key}")
                del self.cache[key]
                self._save_cache()
        return None

    def set(self, key: str, content: Dict[str, Any]):
        """Store content in cache with current timestamp.
        
        Args:
            key: Cache key (typically a URL)
            content: Content to cache
        """
        self.cache[key] = {
            'content': content,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache()

    def clear(self):
        """Clear all cached content."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)