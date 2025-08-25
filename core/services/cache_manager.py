"""
Cache Manager for JakeyBot

This module provides intelligent caching for frequently accessed data
to improve performance and reduce database/API calls.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""

    value: Any
    created_at: float
    accessed_at: float
    access_count: int
    ttl: Optional[int] = None  # Time to live in seconds

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def update_access(self):
        """Update access statistics."""
        self.accessed_at = time.time()
        self.access_count += 1


class CacheManager:
    """
    Intelligent caching system with TTL, LRU eviction, and statistics.

    Features:
    - Time-based expiration (TTL)
    - LRU eviction for memory management
    - Access statistics and analytics
    - Automatic cleanup of expired entries
    - Configurable cache sizes
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_requests": 0,
        }

        # Initialize cleanup task (will be started later when event loop is available)
        self._cleanup_task = None

    def _start_cleanup_task(self):
        """Start the background cleanup task."""
        # Only create the task if we're in an event loop
        try:
            loop = asyncio.get_running_loop()

            async def cleanup_loop():
                while True:
                    try:
                        await asyncio.sleep(60)  # Clean up every minute
                        self._cleanup_expired_entries()
                    except Exception as e:
                        logging.error(f"Error in cache cleanup: {e}")

            self._cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running, will start later
            self._cleanup_task = None

    async def start_cleanup_task(self):
        """Start the background cleanup task if not already running."""
        if self._cleanup_task is None:
            # Use the current event loop to create the task
            try:
                loop = asyncio.get_running_loop()

                async def cleanup_loop():
                    while True:
                        try:
                            await asyncio.sleep(60)  # Clean up every minute
                            self._cleanup_expired_entries()
                        except Exception as e:
                            logging.error(f"Error in cache cleanup: {e}")

                self._cleanup_task = loop.create_task(cleanup_loop())
            except RuntimeError:
                # No event loop running, will start later
                self._cleanup_task = None

    def _cleanup_expired_entries(self):
        """Remove expired cache entries."""
        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]
            self.stats["expirations"] += 1

        if expired_keys:
            logging.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _evict_lru(self):
        """Evict least recently used entries to make room."""
        while len(self.cache) >= self.max_size:
            # Remove the oldest entry (least recently used)
            key, entry = self.cache.popitem(last=False)
            self.stats["evictions"] += 1
            logging.debug(f"Evicted cache entry: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        self.stats["total_requests"] += 1

        if key not in self.cache:
            self.stats["misses"] += 1
            return default

        entry = self.cache[key]

        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            self.stats["misses"] += 1
            self.stats["expirations"] += 1
            return default

        # Update access statistics
        entry.update_access()

        # Move to end (most recently used)
        self.cache.move_to_end(key)

        self.stats["hits"] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        # Remove existing entry if present
        if key in self.cache:
            del self.cache[key]

        # Create new cache entry
        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=1,
            ttl=ttl or self.default_ttl,
        )

        # Add to cache
        self.cache[key] = entry

        # Evict if necessary
        if len(self.cache) > self.max_size:
            self._evict_lru()

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logging.info("Cache cleared")

    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is valid
        """
        if key not in self.cache:
            return False

        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return False

        return True

    def get_or_set(
        self, key: str, default_func: callable, ttl: Optional[int] = None
    ) -> Any:
        """
        Get a value from cache, or set it using a function if not found.

        Args:
            key: Cache key
            default_func: Function to call if key not found
            ttl: Time to live in seconds

        Returns:
            Cached value or newly computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        # Compute new value
        try:
            value = default_func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logging.error(f"Error computing cache value for {key}: {e}")
            return None

    async def get_or_set_async(
        self, key: str, default_func: callable, ttl: Optional[int] = None
    ) -> Any:
        """
        Async version of get_or_set.

        Args:
            key: Cache key
            default_func: Async function to call if key not found
            ttl: Time to live in seconds

        Returns:
            Cached value or newly computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        # Compute new value
        try:
            value = await default_func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logging.error(f"Error computing async cache value for {key}: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        hit_rate = 0
        if self.stats["total_requests"] > 0:
            hit_rate = self.stats["hits"] / self.stats["total_requests"]

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "expirations": self.stats["expirations"],
            "total_requests": self.stats["total_requests"],
        }

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific cache key.

        Args:
            key: Cache key

        Returns:
            Dictionary with key information or None if not found
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        return {
            "key": key,
            "created_at": datetime.fromtimestamp(entry.created_at),
            "accessed_at": datetime.fromtimestamp(entry.accessed_at),
            "access_count": entry.access_count,
            "ttl": entry.ttl,
            "is_expired": entry.is_expired(),
            "age_seconds": time.time() - entry.created_at,
        }

    async def cleanup(self):
        """Clean up resources when shutting down."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self.clear()
        try:
            from core.services.colored_logging import log_success

            log_success("Cache manager cleanup completed")
        except ImportError:
            logging.info("Cache manager cleanup completed")


# Global cache manager instance
cache_manager = CacheManager()


async def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    await cache_manager.start_cleanup_task()
    return cache_manager


async def cleanup_cache():
    """Cleanup function for the cache manager."""
    await cache_manager.cleanup()


# Convenience functions
def cache_get(key: str, default: Any = None) -> Any:
    """Get a value from the global cache."""
    return cache_manager.get(key, default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Set a value in the global cache."""
    cache_manager.set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete a key from the global cache."""
    return cache_manager.delete(key)


def cache_exists(key: str) -> bool:
    """Check if a key exists in the global cache."""
    return cache_manager.exists(key)


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache_manager.get_stats()
