import logging


class JakeyBotError(Exception):
    """Base exception for JakeyBot with error codes and context."""

    def __init__(self, message: str, error_code: str = None, context: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self):
        if self.error_code != "UNKNOWN_ERROR":
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(JakeyBotError):
    """Raised when configuration is invalid or missing required values."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "CONFIG_ERROR", context)


class DatabaseError(JakeyBotError):
    """Raised when database operations fail."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "DATABASE_ERROR", context)


class APIError(JakeyBotError):
    """Raised when external API calls fail."""

    def __init__(self, message: str, api_provider: str = None, context: dict = None):
        self.api_provider = api_provider
        context = context or {}
        if api_provider:
            context["api_provider"] = api_provider
        super().__init__(message, "API_ERROR", context)


class AuthenticationError(JakeyBotError):
    """Raised when authentication fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "AUTH_ERROR", context)


class RateLimitError(JakeyBotError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, retry_after: int = None, context: dict = None):
        self.retry_after = retry_after
        context = context or {}
        if retry_after:
            context["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR", context)


class ValidationError(JakeyBotError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, field: str = None, value: any = None, context: dict = None
    ):
        self.field = field
        self.value = value
        context = context or {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", context)


class PermissionError(JakeyBotError):
    """Raised when user lacks required permissions."""

    def __init__(
        self, message: str, required_permissions: list = None, context: dict = None
    ):
        self.required_permissions = required_permissions or []
        context = context or {}
        if required_permissions:
            context["required_permissions"] = required_permissions
        super().__init__(message, "PERMISSION_ERROR", context)


class ResourceNotFoundError(JakeyBotError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: str = None,
        resource_id: str = None,
        context: dict = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        context = context or {}
        if resource_type:
            context["resource_type"] = resource_type
        if resource_id:
            context["resource_id"] = resource_id
        super().__init__(message, "RESOURCE_NOT_FOUND", context)


class TimeoutError(JakeyBotError):
    """Raised when operations timeout."""

    def __init__(self, message: str, timeout_seconds: int = None, context: dict = None):
        self.timeout_seconds = timeout_seconds
        context = context or {}
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        super().__init__(message, "TIMEOUT_ERROR", context)


class ConcurrentRequestError(JakeyBotError):
    """Raised when multiple requests are made concurrently."""

    def __init__(
        self,
        message: str = "Another request is already in progress",
        context: dict = None,
    ):
        super().__init__(message, "CONCURRENT_REQUEST_ERROR", context)


class HistoryDatabaseError(JakeyBotError):
    """Raised when chat history database operations fail."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "HISTORY_DATABASE_ERROR", context)


class CustomErrorMessage(JakeyBotError):
    """Raised for user-facing custom error messages."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "CUSTOM_ERROR", context)


class ModelAPIKeyUnset(JakeyBotError):
    """Raised when required AI model API keys are not set."""

    def __init__(self, message: str, model_provider: str = None, context: dict = None):
        self.model_provider = model_provider
        context = context or {}
        if model_provider:
            context["model_provider"] = model_provider
        super().__init__(message, "MODEL_API_KEY_UNSET", context)


class PollOffTopicRefusal(JakeyBotError):
    """Raised when a poll is refused due to being off-topic."""

    def __init__(self, message: str = "Poll refused: off-topic", context: dict = None):
        super().__init__(message, "POLL_OFF_TOPIC_REFUSAL", context)


# Error handler utilities
class ErrorHandler:
    """Centralized error handling utilities."""

    @staticmethod
    def log_error(error: Exception, context: dict = None):
        """Log an error with context information."""
        context = context or {}

        if isinstance(error, JakeyBotError):
            logging.error(
                f"JakeyBot Error [{error.error_code}]: {error.message}",
                extra={
                    "error_code": error.error_code,
                    "context": error.context,
                    "additional_context": context,
                },
            )
        else:
            logging.error(
                f"Unexpected error: {str(error)}",
                extra={"error_type": type(error).__name__, "context": context},
                exc_info=True,
            )

    @staticmethod
    def format_user_message(error: Exception) -> str:
        """Format an error message for user display."""
        if isinstance(error, JakeyBotError):
            if error.error_code == "CUSTOM_ERROR":
                return error.message
            elif error.error_code == "PERMISSION_ERROR":
                return f"❌ **Permission Denied**: {error.message}"
            elif error.error_code == "VALIDATION_ERROR":
                return f"⚠️ **Invalid Input**: {error.message}"
            elif error.error_code == "RATE_LIMIT_ERROR":
                return f"⏰ **Rate Limited**: {error.message}"
            elif error.error_code == "TIMEOUT_ERROR":
                return f"⏱️ **Timeout**: {error.message}"
            elif error.error_code == "CONCURRENT_REQUEST_ERROR":
                return f"🔄 **Busy**: {error.message}"
            else:
                return f"❌ **Error**: {error.message}"
        else:
            return (
                "❌ **Unexpected Error**: Something went wrong. Please try again later."
            )

    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if an operation should be retried."""
        if isinstance(error, RateLimitError):
            return True
        elif isinstance(error, TimeoutError):
            return True
        elif isinstance(error, APIError):
            # Retry API errors that aren't authentication or validation issues
            return error.error_code not in ["AUTH_ERROR", "VALIDATION_ERROR"]
        return False


# Convenience functions
def log_and_raise(error: Exception, context: dict = None):
    """Log an error and re-raise it."""
    ErrorHandler.log_error(error, context)
    raise error


def handle_error(error: Exception, context: dict = None) -> str:
    """Handle an error and return a user-friendly message."""
    ErrorHandler.log_error(error, context)
    return ErrorHandler.format_user_message(error)


__all__ = [
    "JakeyBotError",
    "ConfigurationError",
    "DatabaseError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "PermissionError",
    "ResourceNotFoundError",
    "TimeoutError",
    "ConcurrentRequestError",
    "HistoryDatabaseError",
    "CustomErrorMessage",
    "ModelAPIKeyUnset",
    "PollOffTopicRefusal",
    "ErrorHandler",
    "log_and_raise",
    "handle_error",
]
