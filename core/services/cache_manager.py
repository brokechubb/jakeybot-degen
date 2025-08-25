"""
Cache Manager for JakeyBot

Provides intelligent caching for API responses, database queries, and frequently accessed data.
Implements LRU (Least Recently Used) eviction policy and TTL (Time To Live) expiration.
"""

import logging
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Union
from threading import Lock
import asyncio
from functools import wraps


class LRUCache:
    """Thread-safe LRU cache with TTL support"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.lock = Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_requests": 0,
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check"""
        with self.lock:
            self.stats["total_requests"] += 1

            if key not in self.cache:
                self.stats["misses"] += 1
                return None

            # Check TTL
            if self._is_expired(key):
                del self.cache[key]
                del self.timestamps[key]
                self.stats["expirations"] += 1
                self.stats["misses"] += 1
                return None

            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.stats["hits"] += 1
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl

            # Evict if key exists
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]

            # Evict oldest if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
                self.stats["evictions"] += 1

            # Add new entry
            self.cache[key] = value
            self.timestamps[key] = time.time() + ttl

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def _is_expired(self, key: str) -> bool:
        """Check if key is expired"""
        return time.time() > self.timestamps.get(key, 0)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (self.stats["hits"] / max(self.stats["total_requests"], 1)) * 100
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate / 100,  # Return as decimal
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "expirations": self.stats["expirations"],
                "total_requests": self.stats["total_requests"],
            }


# Global cache instances
api_cache = LRUCache(max_size=500, default_ttl=300)  # 5 minutes for API responses
db_cache = LRUCache(max_size=200, default_ttl=600)  # 10 minutes for DB queries
model_cache = LRUCache(max_size=50, default_ttl=1800)  # 30 minutes for model instances


def cache_stats() -> Dict[str, Any]:
    """Get combined cache statistics"""
    return {
        "api_cache": api_cache.get_stats(),
        "db_cache": db_cache.get_stats(),
        "model_cache": model_cache.get_stats(),
        "total_size": api_cache.get_stats()["size"]
        + db_cache.get_stats()["size"]
        + model_cache.get_stats()["size"],
        "total_max_size": api_cache.max_size + db_cache.max_size + model_cache.max_size,
    }


def cached(ttl: Optional[int] = None, cache_instance: Optional[LRUCache] = None):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = (
                f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Use specified cache or default to API cache
            cache = cache_instance or api_cache

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = (
                f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Use specified cache or default to API cache
            cache = cache_instance or api_cache

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Cache management functions
def clear_api_cache() -> None:
    """Clear API response cache"""
    api_cache.clear()
    logging.info("API cache cleared")


def clear_db_cache() -> None:
    """Clear database query cache"""
    db_cache.clear()
    logging.info("Database cache cleared")


def clear_model_cache() -> None:
    """Clear model instance cache"""
    model_cache.clear()
    logging.info("Model cache cleared")


def clear_all_caches() -> None:
    """Clear all caches"""
    clear_api_cache()
    clear_db_cache()
    clear_model_cache()
    logging.info("All caches cleared")


# Performance monitoring
class CacheMonitor:
    """Monitor cache performance and provide insights"""

    @staticmethod
    def get_performance_report() -> Dict[str, Any]:
        """Generate comprehensive cache performance report"""
        stats = cache_stats()

        # Calculate efficiency metrics
        total_hits = sum(
            cache["hits"]
            for cache in [stats["api_cache"], stats["db_cache"], stats["model_cache"]]
        )
        total_requests = sum(
            cache["total_requests"]
            for cache in [stats["api_cache"], stats["db_cache"], stats["model_cache"]]
        )
        overall_hit_rate = total_hits / max(total_requests, 1)

        # Memory usage estimation (rough)
        estimated_memory_mb = (
            stats["total_size"] * 0.1
        )  # Rough estimate: 100KB per cache entry

        return {
            "overall_hit_rate": overall_hit_rate,
            "total_entries": stats["total_size"],
            "memory_usage_mb": estimated_memory_mb,
            "cache_efficiency": "High"
            if overall_hit_rate > 0.7
            else "Medium"
            if overall_hit_rate > 0.4
            else "Low",
            "recommendations": CacheMonitor._get_recommendations(stats),
        }

    @staticmethod
    def _get_recommendations(stats: Dict[str, Any]) -> list:
        """Get cache optimization recommendations"""
        recommendations = []

        for cache_name, cache_stats in [
            ("API", stats["api_cache"]),
            ("DB", stats["db_cache"]),
            ("Model", stats["model_cache"]),
        ]:
            hit_rate = cache_stats["hit_rate"]

            if hit_rate < 0.3:
                recommendations.append(
                    f"Consider increasing {cache_name} cache TTL (current hit rate: {hit_rate:.1%})"
                )
            elif hit_rate > 0.9:
                recommendations.append(
                    f"Consider increasing {cache_name} cache size (current hit rate: {hit_rate:.1%})"
                )

            if cache_stats["evictions"] > cache_stats["hits"] * 0.1:
                recommendations.append(
                    f"Consider increasing {cache_name} cache max size (high eviction rate)"
                )

        return recommendations


# Factory function for cache manager
def get_cache_manager():
    """Get the cache manager instance"""
    return {
        "api_cache": api_cache,
        "db_cache": db_cache,
        "model_cache": model_cache,
        "cache_stats": cache_stats,
        "clear_all_caches": clear_all_caches,
        "CacheMonitor": CacheMonitor,
    }
