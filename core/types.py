"""
Type definitions and interfaces for JakeyBot.

This module provides comprehensive type hints and interfaces
for all major components of the bot.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable, Coroutine, Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    NewType,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

# Type aliases for common types
UserId = NewType("UserId", str)
GuildId = NewType("GuildId", str)
ChannelId = NewType("ChannelId", str)
MessageId = NewType("MessageId", str)
CommandName = NewType("CommandName", str)
ApiKey = NewType("ApiKey", str)
DatabaseUrl = NewType("DatabaseUrl", str)

# Generic type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Discord-related types
DiscordUser = Any  # discord.User
DiscordGuild = Any  # discord.Guild
DiscordChannel = Any  # discord.Channel
DiscordMessage = Any  # discord.Message
DiscordContext = Any  # discord.ext.commands.Context

# Database types
DocumentId = NewType("DocumentId", str)
CollectionName = NewType("CollectionName", str)
DatabaseName = NewType("DatabaseName", str)

# AI Model types
ModelProvider = Literal[
    "gemini",
    "openai",
    "anthropic",
    "mistral",
    "azure",
    "xai",
    "kimi",
    "openrouter",
    "groq",
]
ModelType = Literal["text", "image", "audio", "multimodal"]
ModelCapability = Literal["chat", "completion", "generation", "analysis"]

# Performance types
PerformanceMetric = Literal["command", "api", "database", "system"]
TimeUnit = Literal["seconds", "milliseconds", "microseconds"]

# Cache types
CacheKey = NewType("CacheKey", str)
CacheValue = TypeVar("CacheValue")
CacheTTL = NewType("CacheTTL", int)

# Rate limiting types
RateLimitType = Literal["user", "command", "global", "guild"]
RateLimitBucket = Literal["user", "guild", "channel", "global"]

# Validation types
ValidationRule = Callable[[Any], bool]
ValidationError = NewType("ValidationError", str)
FieldName = NewType("FieldName", str)

# Configuration types
EnvironmentName = Literal["development", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# File types
FileExtension = Literal[
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".mp3",
    ".wav",
    ".ogg",
    ".flac",
    ".m4a",
    ".txt",
    ".md",
    ".pdf",
    ".doc",
    ".docx",
]
FileSize = NewType("FileSize", int)
FilePath = Union[str, Path]

# HTTP types
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HttpStatus = Literal[200, 201, 204, 400, 401, 403, 404, 429, 500, 502, 503]
Url = NewType("Url", str)

# Async types
AsyncFunction = TypeVar("AsyncFunction", bound=Callable[..., Coroutine[Any, Any, Any]])
AsyncContextManager = TypeVar(
    "AsyncContextManager", bound=Callable[..., AsyncIterator[Any]]
)


# Protocol definitions
class DatabaseConnection(Protocol):
    """Protocol for database connections."""

    async def close(self) -> None: ...
    async def ping(self) -> bool: ...
    async def is_connected(self) -> bool: ...


class CacheBackend(Protocol[K, V]):
    """Protocol for cache backends."""

    async def get(self, key: K) -> Optional[V]: ...
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> None: ...
    async def delete(self, key: K) -> bool: ...
    async def exists(self, key: K) -> bool: ...
    async def clear(self) -> None: ...


class RateLimiter(Protocol):
    """Protocol for rate limiters."""

    async def check_rate_limit(
        self, user_id: UserId, command: Optional[CommandName] = None
    ) -> None: ...
    async def record_request(
        self, user_id: UserId, command: Optional[CommandName] = None
    ) -> None: ...
    async def acquire_slot(
        self, user_id: UserId, command: Optional[CommandName] = None
    ) -> None: ...


class InputValidator(Protocol):
    """Protocol for input validators."""

    def validate_discord_id(self, value: Any, id_type: str = "user") -> str: ...
    def validate_url(self, value: Any, url_type: str = "general") -> str: ...
    def validate_message_content(
        self, value: Any, max_length: Optional[int] = None
    ) -> str: ...
    def sanitize_html(self, content: str) -> str: ...


class PerformanceMonitor(Protocol):
    """Protocol for performance monitors."""

    def time_command(self, command_name: CommandName) -> Callable: ...
    def time_api_call(self, api_name: str) -> Callable: ...
    def time_db_operation(self, operation_name: str) -> Callable: ...
    def get_performance_summary(self) -> Dict[str, Any]: ...


# Data classes for structured data
@dataclass(frozen=True)
class ModelConfig:
    """Configuration for an AI model."""

    provider: ModelProvider
    model_name: str
    api_key: ApiKey
    model_type: ModelType
    capabilities: List[ModelCapability]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    is_default: bool = False


@dataclass(frozen=True)
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests: int
    time_window: int  # in seconds
    burst_size: int = 1
    bucket_type: RateLimitBucket = "user"


@dataclass(frozen=True)
class CacheConfig:
    """Configuration for caching."""

    max_size: int = 1000
    default_ttl: int = 300  # 5 minutes
    cleanup_interval: int = 60  # 1 minute
    enable_compression: bool = False


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration for database connections."""

    url: DatabaseUrl
    database_name: DatabaseName
    max_pool_size: int = 100
    connection_timeout: int = 5000  # milliseconds
    server_selection_timeout: int = 5000  # milliseconds


@dataclass(frozen=True)
class LoggingConfig:
    """Configuration for logging."""

    level: LogLevel = "INFO"
    format_string: Optional[str] = None
    date_format: Optional[str] = None
    enable_colors: bool = True
    log_to_file: bool = False
    log_file_path: Optional[FilePath] = None


@dataclass(frozen=True)
class BotConfig:
    """Main bot configuration."""

    token: str
    prefix: str
    intents: List[str]
    environment: EnvironmentName = "development"
    debug_mode: bool = False
    enable_metrics: bool = True
    enable_caching: bool = True
    enable_rate_limiting: bool = True


# Enum definitions
class CommandCategory(Enum):
    """Categories for bot commands."""

    ADMIN = "admin"
    AI = "ai"
    GAMING = "gaming"
    UTILITY = "utility"
    FUN = "fun"
    MODERATION = "moderation"
    ECONOMY = "economy"


class PermissionLevel(Enum):
    """Permission levels for commands."""

    EVERYONE = 0
    MODERATOR = 1
    ADMINISTRATOR = 2
    OWNER = 3


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Generic container types
@dataclass
class PaginatedResult(Generic[T]):
    """Generic paginated result container."""

    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class AsyncResult(Generic[T]):
    """Generic async result container."""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Callback types
CommandCallback = Callable[[DiscordContext, ...], Coroutine[None, None, None]]
ErrorCallback = Callable[[Exception, DiscordContext], Coroutine[None, None, None]]
EventCallback = Callable[[Any], Coroutine[None, None, None]]

# Decorator types
Decorator = Callable[[Callable], Callable]
AsyncDecorator = Callable[[AsyncFunction], AsyncFunction]

# Context manager types
AsyncResource = TypeVar("AsyncResource", bound=AsyncContextManager)

# Utility types
JsonValue = Union[
    str, int, float, bool, None, List["JsonValue"], Dict[str, "JsonValue"]
]
JsonDict = Dict[str, JsonValue]


# Type checking helpers
def is_valid_user_id(value: Any) -> bool:
    """Check if a value is a valid Discord user ID."""
    if not isinstance(value, str):
        return False
    return value.isdigit() and len(value) >= 17 and len(value) <= 19


def is_valid_guild_id(value: Any) -> bool:
    """Check if a value is a valid Discord guild ID."""
    return is_valid_user_id(value)


def is_valid_channel_id(value: Any) -> bool:
    """Check if a value is a valid Discord channel ID."""
    return is_valid_user_id(value)


def is_valid_api_key(value: Any) -> bool:
    """Check if a value is a valid API key."""
    if not isinstance(value, str):
        return False
    return len(value) > 0 and not value.isspace()


# Type conversion helpers
def to_user_id(value: Any) -> UserId:
    """Convert a value to a UserId."""
    if not is_valid_user_id(value):
        raise ValueError(f"Invalid user ID: {value}")
    return UserId(str(value))


def to_guild_id(value: Any) -> GuildId:
    """Convert a value to a GuildId."""
    if not is_valid_guild_id(value):
        raise ValueError(f"Invalid guild ID: {value}")
    return GuildId(str(value))


def to_channel_id(value: Any) -> ChannelId:
    """Convert a value to a ChannelId."""
    if not is_valid_channel_id(value):
        raise ValueError(f"Invalid channel ID: {value}")
    return ChannelId(str(value))


# Async utility types
AsyncTask = asyncio.Task[Any]
AsyncFuture = asyncio.Future[Any]

# Event loop types
EventLoop = asyncio.AbstractEventLoop

# Time types
Timestamp = Union[int, float, datetime]
Duration = Union[int, float]  # in seconds


# Configuration validation
def validate_bot_config(config: BotConfig) -> bool:
    """Validate bot configuration."""
    if not config.token:
        return False
    if not config.prefix:
        return False
    if not config.intents:
        return False
    return True


def validate_database_config(config: DatabaseConfig) -> bool:
    """Validate database configuration."""
    if not config.url:
        return False
    if not config.database_name:
        return False
    if config.max_pool_size <= 0:
        return False
    return True


# Export all types
__all__ = [
    # Type aliases
    "UserId",
    "GuildId",
    "ChannelId",
    "MessageId",
    "CommandName",
    "ApiKey",
    "DatabaseUrl",
    "DocumentId",
    "CollectionName",
    "DatabaseName",
    "CacheKey",
    "CacheValue",
    "CacheTTL",
    "ValidationError",
    "FieldName",
    "FileExtension",
    "FileSize",
    "FilePath",
    "Url",
    # Generic types
    "T",
    "K",
    "V",
    "AsyncFunction",
    "AsyncContextManager",
    "AsyncResource",
    # Discord types
    "DiscordUser",
    "DiscordGuild",
    "DiscordChannel",
    "DiscordMessage",
    "DiscordContext",
    # AI types
    "ModelProvider",
    "ModelType",
    "ModelCapability",
    # Performance types
    "PerformanceMetric",
    "TimeUnit",
    # Rate limiting types
    "RateLimitType",
    "RateLimitBucket",
    # Validation types
    "ValidationRule",
    # Configuration types
    "EnvironmentName",
    "LogLevel",
    # HTTP types
    "HttpMethod",
    "HttpStatus",
    # Async types
    "AsyncIterator",
    "Coroutine",
    "AsyncTask",
    "AsyncFuture",
    "EventLoop",
    # Protocol definitions
    "DatabaseConnection",
    "CacheBackend",
    "RateLimiter",
    "InputValidator",
    "PerformanceMonitor",
    # Data classes
    "ModelConfig",
    "RateLimitConfig",
    "CacheConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "BotConfig",
    "PaginatedResult",
    "AsyncResult",
    # Enums
    "CommandCategory",
    "PermissionLevel",
    "ErrorSeverity",
    # Callback types
    "CommandCallback",
    "ErrorCallback",
    "EventCallback",
    # Decorator types
    "Decorator",
    "AsyncDecorator",
    # Utility types
    "JsonValue",
    "JsonDict",
    "Timestamp",
    "Duration",
    # Helper functions
    "is_valid_user_id",
    "is_valid_guild_id",
    "is_valid_channel_id",
    "is_valid_api_key",
    "to_user_id",
    "to_guild_id",
    "to_channel_id",
    "validate_bot_config",
    "validate_database_config",
]
