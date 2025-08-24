"""
Rate Limiting System for JakeyBot

This module provides rate limiting functionality to prevent abuse
and ensure fair usage of bot resources.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Dict, Deque, Optional, Tuple
from dataclasses import dataclass
from core.exceptions import RateLimitError


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit rule."""

    max_requests: int
    time_window: int  # in seconds
    burst_size: int = 1  # allow burst of requests


class RateLimiter:
    """
    Rate limiter implementation using sliding window algorithm.

    Features:
    - Sliding window rate limiting
    - Per-user and per-command limits
    - Burst allowance
    - Automatic cleanup of expired entries
    """

    def __init__(self):
        self.limits: Dict[str, RateLimitConfig] = {}
        self.user_requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
        self.command_requests: Dict[str, Dict[str, Deque[float]]] = defaultdict(
            lambda: defaultdict(lambda: deque())
        )
        self.global_requests: Deque[float] = deque()

        # Default rate limits
        self._setup_default_limits()

        # Start cleanup task
        self._cleanup_task = None
        # Don't start cleanup task during initialization - will be started when needed

    def _setup_default_limits(self):
        """Setup default rate limiting rules."""
        self.limits = {
            # Global limits
            "global": RateLimitConfig(max_requests=100, time_window=60, burst_size=10),
            # Command-specific limits
            "chat": RateLimitConfig(max_requests=20, time_window=60, burst_size=5),
            "image_gen": RateLimitConfig(max_requests=5, time_window=60, burst_size=2),
            "code_execution": RateLimitConfig(
                max_requests=10, time_window=300, burst_size=3
            ),
            "web_search": RateLimitConfig(
                max_requests=15, time_window=60, burst_size=5
            ),
            "file_upload": RateLimitConfig(
                max_requests=10, time_window=300, burst_size=3
            ),
            # User-specific limits
            "user_chat": RateLimitConfig(
                max_requests=50, time_window=300, burst_size=10
            ),
            "user_image_gen": RateLimitConfig(
                max_requests=10, time_window=300, burst_size=3
            ),
            "user_code_execution": RateLimitConfig(
                max_requests=20, time_window=600, burst_size=5
            ),
        }

    def _start_cleanup_task(self):
        """Start the background cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Clean up every 5 minutes
                    self._cleanup_expired_entries()
                except Exception as e:
                    logging.error(f"Error in rate limiter cleanup: {e}")

        try:
            self._cleanup_task = asyncio.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running, will start later
            self._cleanup_task = None

    def _cleanup_expired_entries(self):
        """Remove expired request timestamps."""
        current_time = time.time()

        # Cleanup global requests
        while self.global_requests and current_time - self.global_requests[0] > 60:
            self.global_requests.popleft()

        # Cleanup user requests
        for user_id in list(self.user_requests.keys()):
            while (
                self.user_requests[user_id]
                and current_time - self.user_requests[user_id][0] > 300
            ):
                self.user_requests[user_id].popleft()

            # Remove empty user entries
            if not self.user_requests[user_id]:
                del self.user_requests[user_id]

        # Cleanup command requests
        for command in list(self.command_requests.keys()):
            for user_id in list(self.command_requests[command].keys()):
                while (
                    self.command_requests[command][user_id]
                    and current_time - self.command_requests[command][user_id][0] > 300
                ):
                    self.command_requests[command][user_id].popleft()

                # Remove empty command entries
                if not self.command_requests[command][user_id]:
                    del self.command_requests[command][user_id]

            # Remove empty command entries
            if not self.command_requests[command]:
                del self.command_requests[command]

    def _check_rate_limit(
        self, requests: Deque[float], config: RateLimitConfig
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if a rate limit has been exceeded.

        Args:
            requests: Queue of request timestamps
            config: Rate limit configuration

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        current_time = time.time()

        # Remove expired timestamps
        while requests and current_time - requests[0] > config.time_window:
            requests.popleft()

        # Check if limit exceeded
        if len(requests) >= config.max_requests:
            # Calculate retry time
            retry_after = int(config.time_window - (current_time - requests[0]))
            return False, max(1, retry_after)

        return True, None

    async def start_cleanup_task(self):
        """Start the background cleanup task if not already running."""
        if self._cleanup_task is None:
            self._start_cleanup_task()

    async def check_rate_limit(self, user_id: str, command: str = None) -> None:
        """
        Check if a user can make a request.

        Args:
            user_id: Discord user ID
            command: Command being executed (optional)

        Raises:
            RateLimitError: If rate limit exceeded
        """
        current_time = time.time()

        # Check global rate limit
        allowed, retry_after = self._check_rate_limit(
            self.global_requests, self.limits["global"]
        )
        if not allowed:
            raise RateLimitError(
                f"Global rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after,
            )

        # Check user-specific rate limit
        allowed, retry_after = self._check_rate_limit(
            self.user_requests[user_id], self.limits["user_chat"]
        )
        if not allowed:
            raise RateLimitError(
                f"User rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after,
            )

        # Check command-specific rate limit
        if command and command in self.limits:
            allowed, retry_after = self._check_rate_limit(
                self.command_requests[command][user_id], self.limits[command]
            )
            if not allowed:
                raise RateLimitError(
                    f"Rate limit exceeded for {command}. Try again in {retry_after} seconds.",
                    retry_after=retry_after,
                )

    def record_request(self, user_id: str, command: str = None):
        """
        Record a successful request.

        Args:
            user_id: Discord user ID
            command: Command executed (optional)
        """
        current_time = time.time()

        # Record global request
        self.global_requests.append(current_time)

        # Record user request
        self.user_requests[user_id].append(current_time)

        # Record command request
        if command:
            self.command_requests[command][user_id].append(current_time)

    async def acquire_slot(self, user_id: str, command: str = None) -> None:
        """
        Acquire a rate limit slot (check + record).

        Args:
            user_id: Discord user ID
            command: Command being executed (optional)

        Raises:
            RateLimitError: If rate limit exceeded
        """
        await self.check_rate_limit(user_id, command)
        self.record_request(user_id, command)

    def get_user_stats(self, user_id: str) -> Dict[str, any]:
        """
        Get rate limiting statistics for a user.

        Args:
            user_id: Discord user ID

        Returns:
            Dictionary with rate limiting statistics
        """
        current_time = time.time()
        stats = {}

        # Global stats
        global_requests = len(
            [t for t in self.global_requests if current_time - t <= 60]
        )
        stats["global"] = {
            "requests_last_minute": global_requests,
            "limit": self.limits["global"].max_requests,
            "remaining": max(0, self.limits["global"].max_requests - global_requests),
        }

        # User stats
        user_requests = len(
            [t for t in self.user_requests[user_id] if current_time - t <= 300]
        )
        stats["user"] = {
            "requests_last_5_minutes": user_requests,
            "limit": self.limits["user_chat"].max_requests,
            "remaining": max(0, self.limits["user_chat"].max_requests - user_requests),
        }

        # Command stats
        stats["commands"] = {}
        for command, config in self.limits.items():
            if command in ["global", "user_chat"]:
                continue

            if (
                command in self.command_requests
                and user_id in self.command_requests[command]
            ):
                cmd_requests = len(
                    [
                        t
                        for t in self.command_requests[command][user_id]
                        if current_time - t <= config.time_window
                    ]
                )
                stats["commands"][command] = {
                    "requests": cmd_requests,
                    "limit": config.max_requests,
                    "remaining": max(0, config.max_requests - cmd_requests),
                    "time_window": config.time_window,
                }

        return stats

    def add_custom_limit(self, name: str, config: RateLimitConfig):
        """
        Add a custom rate limit rule.

        Args:
            name: Name of the rate limit rule
            config: Rate limit configuration
        """
        self.limits[name] = config
        logging.info(
            f"Added custom rate limit: {name} - {config.max_requests} requests per {config.time_window}s"
        )

    async def cleanup(self):
        """Clean up resources when shutting down."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Clear all data
        self.user_requests.clear()
        self.command_requests.clear()
        self.global_requests.clear()
        logging.info("Rate limiter cleanup completed")


# Global rate limiter instance
rate_limiter = RateLimiter()


async def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    await rate_limiter.start_cleanup_task()
    return rate_limiter


async def cleanup_rate_limiter():
    """Cleanup function for the rate limiter."""
    await rate_limiter.cleanup()
