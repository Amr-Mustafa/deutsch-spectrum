"""Caching layer for POS analysis results."""
from cachetools import TTLCache
import hashlib
import json
from typing import Optional, List
from .models import Token


class AnalysisCache:
    """Cache for storing POS analysis results."""

    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        """
        Initialize the cache.

        Args:
            maxsize: Maximum number of cached items
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def _generate_key(self, text: str) -> str:
        """Generate a cache key from text."""
        # Use hash of the text as the key
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get(self, text: str) -> Optional[List[Token]]:
        """
        Retrieve cached analysis result.

        Args:
            text: The text that was analyzed

        Returns:
            List of Token objects if cached, None otherwise
        """
        key = self._generate_key(text)
        return self.cache.get(key)

    def set(self, text: str, tokens: List[Token]) -> None:
        """
        Store analysis result in cache.

        Args:
            text: The text that was analyzed
            tokens: The analysis result
        """
        key = self._generate_key(text)
        self.cache[key] = tokens

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'maxsize': self.cache.maxsize,
            'ttl': self.cache.ttl
        }


# Global cache instance
analysis_cache = AnalysisCache()
