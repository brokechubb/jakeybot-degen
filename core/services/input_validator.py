"""
Input Validation and Sanitization for JakeyBot

This module provides comprehensive input validation and sanitization
to prevent security issues and ensure data integrity.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from core.exceptions import ValidationError


class InputValidator:
    """Comprehensive input validation and sanitization."""

    # Discord-specific patterns
    DISCORD_USER_ID_PATTERN = r"^\d{17,19}$"
    DISCORD_CHANNEL_ID_PATTERN = r"^\d{17,19}$"
    DISCORD_GUILD_ID_PATTERN = r"^\d{17,19}$"
    DISCORD_MENTION_PATTERN = r"<@!?(\d{17,19})>"

    # URL patterns
    URL_PATTERN = r"^https?://[^\s/$.?#].[^\s]*$"
    IMAGE_URL_PATTERN = (
        r"^https?://[^\s/$.?#].[^\s]*(?:\.(?:jpg|jpeg|png|gif|webp|bmp))$"
    )

    # File patterns
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
    ALLOWED_DOCUMENT_EXTENSIONS = {".txt", ".md", ".pdf", ".doc", ".docx"}

    # Content patterns
    MAX_MESSAGE_LENGTH = 4000
    MAX_FILENAME_LENGTH = 100
    MAX_URL_LENGTH = 2048

    def __init__(self):
        self.compiled_patterns = {
            "discord_user_id": re.compile(self.DISCORD_USER_ID_PATTERN),
            "discord_channel_id": re.compile(self.DISCORD_CHANNEL_ID_PATTERN),
            "discord_guild_id": re.compile(self.DISCORD_GUILD_ID_PATTERN),
            "discord_mention": re.compile(self.DISCORD_MENTION_PATTERN),
            "url": re.compile(self.URL_PATTERN),
            "image_url": re.compile(self.IMAGE_URL_PATTERN),
        }

    def validate_discord_id(self, value: Any, id_type: str = "user") -> str:
        """
        Validate Discord ID format.

        Args:
            value: The ID to validate
            id_type: Type of ID (user, channel, guild)

        Returns:
            Validated ID string

        Raises:
            ValidationError: If ID is invalid
        """
        if not value:
            raise ValidationError(f"Discord {id_type} ID is required", field=id_type)

        value_str = str(value).strip()

        if id_type == "user":
            pattern = self.compiled_patterns["discord_user_id"]
        elif id_type == "channel":
            pattern = self.compiled_patterns["discord_channel_id"]
        elif id_type == "guild":
            pattern = self.compiled_patterns["discord_guild_id"]
        else:
            raise ValidationError(f"Unknown Discord ID type: {id_type}", field=id_type)

        if not pattern.match(value_str):
            raise ValidationError(
                f"Invalid Discord {id_type} ID format: {value_str}",
                field=id_type,
                value=value_str,
            )

        return value_str

    def validate_url(self, value: Any, url_type: str = "general") -> str:
        """
        Validate URL format and safety.

        Args:
            value: The URL to validate
            url_type: Type of URL (general, image, audio, document)

        Returns:
            Validated URL string

        Raises:
            ValidationError: If URL is invalid
        """
        if not value:
            raise ValidationError("URL is required", field="url")

        url_str = str(value).strip()

        # Check length
        if len(url_str) > self.MAX_URL_LENGTH:
            raise ValidationError(
                f"URL too long (max {self.MAX_URL_LENGTH} characters)",
                field="url",
                value=url_str,
            )

        # Check basic format
        if not self.compiled_patterns["url"].match(url_str):
            raise ValidationError(
                f"Invalid URL format: {url_str}", field="url", value=url_str
            )

        # Parse URL for additional validation
        try:
            parsed = urlparse(url_str)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(
                    f"Invalid URL structure: {url_str}", field="url", value=url_str
                )
        except Exception as e:
            raise ValidationError(
                f"URL parsing failed: {str(e)}", field="url", value=url_str
            )

        # Type-specific validation
        if url_type == "image":
            if not self.compiled_patterns["image_url"].match(url_str):
                raise ValidationError(
                    f"Invalid image URL: {url_str}", field="url", value=url_str
                )

        return url_str

    def validate_filename(self, value: Any, allowed_extensions: set = None) -> str:
        """
        Validate filename format and safety.

        Args:
            value: The filename to validate
            allowed_extensions: Set of allowed file extensions

        Returns:
            Validated filename string

        Raises:
            ValidationError: If filename is invalid
        """
        if not value:
            raise ValidationError("Filename is required", field="filename")

        filename = str(value).strip()

        # Check length
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise ValidationError(
                f"Filename too long (max {self.MAX_FILENAME_LENGTH} characters)",
                field="filename",
                value=filename,
            )

        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
        if any(char in filename for char in dangerous_chars):
            raise ValidationError(
                f"Filename contains dangerous characters: {filename}",
                field="filename",
                value=filename,
            )

        # Check extension if specified
        if allowed_extensions:
            file_ext = self._get_file_extension(filename)
            if file_ext.lower() not in allowed_extensions:
                raise ValidationError(
                    f"File extension not allowed: {file_ext}. Allowed: {', '.join(allowed_extensions)}",
                    field="filename",
                    value=filename,
                )

        return filename

    def validate_message_content(self, value: Any, max_length: int = None) -> str:
        """
        Validate message content for safety and length.

        Args:
            value: The message content to validate
            max_length: Maximum allowed length

        Returns:
            Validated message content

        Raises:
            ValidationError: If content is invalid
        """
        if value is None:
            raise ValidationError("Message content is required", field="content")

        content = str(value).strip()
        max_len = max_length or self.MAX_MESSAGE_LENGTH

        # Check length
        if len(content) > max_len:
            raise ValidationError(
                f"Message too long (max {max_len} characters)",
                field="content",
                value=content[:100] + "..." if len(content) > 100 else content,
            )

        # Check for empty content
        if not content:
            raise ValidationError("Message content cannot be empty", field="content")

        # Check for potentially dangerous content
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript protocol
            r"data:text/html",  # Data URLs
            r"vbscript:",  # VBScript protocol
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValidationError(
                    "Message content contains potentially dangerous content",
                    field="content",
                    value=content[:100] + "..." if len(content) > 100 else content,
                )

        return content

    def validate_integer(
        self,
        value: Any,
        min_value: int = None,
        max_value: int = None,
        field_name: str = "value",
    ) -> int:
        """
        Validate integer value within range.

        Args:
            value: The value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of the field for error messages

        Returns:
            Validated integer

        Raises:
            ValidationError: If value is invalid
        """
        if value is None:
            raise ValidationError(f"{field_name} is required", field=field_name)

        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name} must be a valid integer", field=field_name, value=value
            )

        if min_value is not None and int_value < min_value:
            raise ValidationError(
                f"{field_name} must be at least {min_value}",
                field=field_name,
                value=int_value,
            )

        if max_value is not None and int_value > max_value:
            raise ValidationError(
                f"{field_name} must be at most {max_value}",
                field=field_name,
                value=int_value,
            )

        return int_value

    def validate_choice(
        self, value: Any, allowed_choices: List[Any], field_name: str = "value"
    ) -> Any:
        """
        Validate that a value is one of the allowed choices.

        Args:
            value: The value to validate
            allowed_choices: List of allowed values
            field_name: Name of the field for error messages

        Returns:
            Validated value

        Raises:
            ValidationError: If value is not in allowed choices
        """
        if value is None:
            raise ValidationError(f"{field_name} is required", field=field_name)

        if value not in allowed_choices:
            raise ValidationError(
                f"{field_name} must be one of: {', '.join(map(str, allowed_choices))}",
                field=field_name,
                value=value,
            )

        return value

    def sanitize_html(self, content: str) -> str:
        """
        Sanitize HTML content by removing dangerous tags and attributes.

        Args:
            content: HTML content to sanitize

        Returns:
            Sanitized HTML content
        """
        # Remove script tags and content
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove dangerous tags
        dangerous_tags = [
            "script",
            "iframe",
            "object",
            "embed",
            "form",
            "input",
            "textarea",
            "select",
        ]
        for tag in dangerous_tags:
            content = re.sub(
                rf"<{tag}[^>]*>.*?</{tag}>",
                "",
                content,
                flags=re.IGNORECASE | re.DOTALL,
            )
            content = re.sub(rf"<{tag}[^>]*/?>", "", content, flags=re.IGNORECASE)

        # Remove dangerous attributes
        dangerous_attrs = [
            "onclick",
            "onload",
            "onerror",
            "onmouseover",
            "javascript:",
            "vbscript:",
        ]
        for attr in dangerous_attrs:
            content = re.sub(rf'{attr}="[^"]*"', "", content, flags=re.IGNORECASE)
            content = re.sub(rf"{attr}='[^']*'", "", content, flags=re.IGNORECASE)

        return content

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if "." not in filename:
            return ""
        return "." + filename.split(".")[-1].lower()

    def validate_file_upload(
        self, filename: str, file_size: int, max_size: int, allowed_types: set
    ) -> Dict[str, any]:
        """
        Validate file upload parameters.

        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            max_size: Maximum allowed file size in bytes
            allowed_types: Set of allowed file types/extensions

        Returns:
            Dictionary with validation results

        Raises:
            ValidationError: If file upload is invalid
        """
        # Validate filename
        validated_filename = self.validate_filename(filename, allowed_types)

        # Validate file size
        if file_size > max_size:
            raise ValidationError(
                f"File too large (max {max_size} bytes)",
                field="file_size",
                value=file_size,
            )

        # Get file type
        file_ext = self._get_file_extension(filename)
        file_type = self._get_file_type(file_ext)

        return {
            "filename": validated_filename,
            "file_size": file_size,
            "file_type": file_type,
            "file_extension": file_ext,
        }

    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension."""
        if extension in self.ALLOWED_IMAGE_EXTENSIONS:
            return "image"
        elif extension in self.ALLOWED_AUDIO_EXTENSIONS:
            return "audio"
        elif extension in self.ALLOWED_DOCUMENT_EXTENSIONS:
            return "document"
        else:
            return "unknown"


# Global validator instance
input_validator = InputValidator()


def get_input_validator() -> InputValidator:
    """Get the global input validator instance."""
    return input_validator


# Convenience functions
def validate_discord_id(value: Any, id_type: str = "user") -> str:
    """Validate Discord ID."""
    return input_validator.validate_discord_id(value, id_type)


def validate_url(value: Any, url_type: str = "general") -> str:
    """Validate URL."""
    return input_validator.validate_url(value, url_type)


def validate_filename(value: Any, allowed_extensions: set = None) -> str:
    """Validate filename."""
    return input_validator.validate_filename(value, allowed_extensions)


def validate_message_content(value: Any, max_length: int = None) -> str:
    """Validate message content."""
    return input_validator.validate_message_content(value, max_length)


def sanitize_html(content: str) -> str:
    """Sanitize HTML content."""
    return input_validator.sanitize_html(content)
