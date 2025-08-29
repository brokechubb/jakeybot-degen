"""
Configuration Validator for JakeyBot

This module validates environment variables and configuration settings
to ensure the bot starts with proper configuration.
"""

import os
import logging
from typing import Dict, List, Optional


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""

    pass


class ConfigValidator:
    """Validates environment variables and configuration settings."""

    # Required environment variables
    REQUIRED_VARS = {
        "TOKEN": "Discord bot token",
        "MONGO_DB_URL": "MongoDB connection string",
    }

    # Optional but recommended environment variables
    RECOMMENDED_VARS = {
        "OPENAI_API_KEY": "OpenAI API key for GPT models",
        "ANTHROPIC_API_KEY": "Anthropic API key for Claude models",
        "MISTRAL_API_KEY": "Mistral API key for Mistral models",
        "AZURE_AI_API_BASE": "Azure AI endpoint for DeepSeek models",
        "AZURE_AI_API_KEY": "Azure AI API key",
    }

    # AI model providers that require API keys
    AI_PROVIDERS = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "MISTRAL_API_KEY",
        "AZURE_AI_API_KEY",
        "XAI_API_KEY",
        "KIMI_API_KEY",
        "OPENROUTER_API_KEY",
        "GROQ_API_KEY",
    ]

    @classmethod
    def validate_all(cls) -> Dict[str, List[str]]:
        """
        Validate all configuration settings.

        Returns:
            Dict containing validation results with 'errors' and 'warnings' lists

        Raises:
            ConfigurationError: If required configuration is missing
        """
        errors = []
        warnings = []

        # Validate required variables
        for var, description in cls.REQUIRED_VARS.items():
            if not os.getenv(var):
                errors.append(
                    f"Missing required environment variable: {var} ({description})"
                )
            elif os.getenv(var) == "INSERT_DISCORD_TOKEN":
                errors.append(
                    f"Please set a valid value for {var} instead of placeholder"
                )

        # Validate MongoDB URL format
        mongo_url = os.getenv("MONGO_DB_URL")
        if mongo_url and not mongo_url.startswith(("mongodb://", "mongodb+srv://")):
            warnings.append(
                "MONGO_DB_URL should start with 'mongodb://' or 'mongodb+srv://'"
            )

        # Check if at least one AI API key is set
        ai_keys_set = [key for key in cls.AI_PROVIDERS if os.getenv(key)]
        if not ai_keys_set:
            warnings.append(
                "No AI API keys found. The bot will have limited functionality."
            )
        else:
            logging.info(f"Found AI API keys for: {', '.join(ai_keys_set)}")

        # Validate timeout configurations
        timeout_vars = [
            "TOOL_TIMEOUT_EXASEARCH",
            "TOOL_TIMEOUT_CODEEXECUTION",
            "TOOL_TIMEOUT_CRYPTOPRICE",
            "TOOL_TIMEOUT_CURRENCYCONVERTER",
            "TOOL_TIMEOUT_DEFAULT",
        ]

        for timeout_var in timeout_vars:
            value = os.getenv(timeout_var)
            if value:
                try:
                    timeout = int(value)
                    if timeout < 30 or timeout > 3600:
                        warnings.append(
                            f"{timeout_var} should be between 30 and 3600 seconds (current: {timeout})"
                        )
                except ValueError:
                    warnings.append(
                        f"{timeout_var} should be a valid integer (current: {value})"
                    )

        # Validate bot configuration
        bot_prefix = os.getenv("BOT_PREFIX", "$")
        if len(bot_prefix) > 5:
            warnings.append("BOT_PREFIX should be short (1-5 characters)")

        # Validate database configuration
        db_name = os.getenv("MONGO_DB_NAME")
        if db_name and not db_name.replace("_", "").isalnum():
            warnings.append(
                "MONGO_DB_NAME should only contain letters, numbers, and underscores"
            )

        # Check for potential security issues
        if os.getenv("SHARED_CHAT_HISTORY", "false").lower() == "true":
            logging.info(
                "SHARED_CHAT_HISTORY is enabled - guilds will share conversation history"
            )

        # Return validation results
        return {"errors": errors, "warnings": warnings}

    @classmethod
    def validate_and_raise(cls):
        """
        Validate configuration and raise ConfigurationError if validation fails.

        Raises:
            ConfigurationError: If required configuration is missing
        """
        results = cls.validate_all()

        # Log warnings
        for warning in results["warnings"]:
            logging.warning(f"Configuration warning: {warning}")

        # Raise error if there are critical issues
        if results["errors"]:
            error_msg = "\n".join(results["errors"])
            raise ConfigurationError(f"Configuration validation failed:\n{error_msg}")

    @classmethod
    def get_config_summary(cls) -> Dict[str, any]:
        """
        Get a summary of current configuration.

        Returns:
            Dict containing configuration summary
        """
        return {
            "bot_name": os.getenv("BOT_NAME", "Jakey Bot"),
            "bot_prefix": os.getenv("BOT_PREFIX", "$"),
            "shared_chat_history": os.getenv("SHARED_CHAT_HISTORY", "false").lower()
            == "true",
            "default_tool": os.getenv("DEFAULT_TOOL", "Memory"),
            "ai_providers_configured": [
                key for key in cls.AI_PROVIDERS if os.getenv(key)
            ],
            "database_configured": bool(os.getenv("MONGO_DB_URL")),
            "azure_storage_configured": bool(
                os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            ),
        }


def validate_configuration():
    """
    Convenience function to validate configuration.

    Raises:
        ConfigurationError: If configuration validation fails
    """
    ConfigValidator.validate_and_raise()


def get_config_summary():
    """
    Convenience function to get configuration summary.

    Returns:
        Dict containing configuration summary
    """
    return ConfigValidator.get_config_summary()
