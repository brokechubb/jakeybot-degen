"""
Decorators for JakeyBot Commands

This module provides decorators for common command functionality
like rate limiting, input validation, and error handling.
"""

import functools
import logging
from typing import Callable, Any, Optional
from discord.ext import commands
from core.exceptions import RateLimitError, ValidationError, JakeyBotError
from core.services.rate_limiter import get_rate_limiter
from core.services.input_validator import get_input_validator


def rate_limit(command_type: str = None, user_id_field: str = "author.id"):
    """
    Decorator to apply rate limiting to commands.

    Args:
        command_type: Type of command for rate limiting (e.g., 'chat', 'image_gen')
        user_id_field: Field path to extract user ID from context

    Usage:
        @rate_limit('chat')
        async def my_command(self, ctx):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Get the context (first argument after self)
                ctx = args[1] if len(args) > 1 else None

                if ctx and hasattr(ctx, "bot") and hasattr(ctx.bot, "rate_limiter"):
                    # Extract user ID
                    user_id = _extract_field_value(ctx, user_id_field)
                    if user_id:
                        # Check rate limit
                        await ctx.bot.rate_limiter.acquire_slot(
                            str(user_id), command_type
                        )

                # Execute the command
                return await func(*args, **kwargs)

            except RateLimitError as e:
                # Handle rate limit errors
                if ctx and hasattr(ctx, "respond"):
                    await ctx.respond(str(e))
                elif ctx and hasattr(ctx, "send"):
                    await ctx.send(str(e))
                else:
                    logging.error(
                        f"Rate limit exceeded but no response method available: {e}"
                    )
                return None

            except Exception as e:
                # Re-raise other exceptions
                raise

        return wrapper

    return decorator


def validate_input(validation_rules: dict):
    """
    Decorator to apply input validation to commands.

    Args:
        validation_rules: Dictionary mapping field names to validation functions

    Usage:
        @validate_input({
            'content': lambda x: validate_message_content(x),
            'user_id': lambda x: validate_discord_id(x, 'user')
        })
        async def my_command(self, ctx, content, user_id):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Get the context and bot
                ctx = args[1] if len(args) > 1 else None
                bot = ctx.bot if ctx else None

                if bot and hasattr(bot, "input_validator"):
                    # Apply validation rules
                    for field_name, validation_func in validation_rules.items():
                        if field_name in kwargs:
                            try:
                                # Apply validation
                                validated_value = validation_func(kwargs[field_name])
                                kwargs[field_name] = validated_value
                            except ValidationError as e:
                                # Handle validation errors
                                if ctx and hasattr(ctx, "respond"):
                                    await ctx.respond(str(e))
                                elif ctx and hasattr(ctx, "send"):
                                    await ctx.send(str(e))
                                else:
                                    logging.error(
                                        f"Validation failed but no response method available: {e}"
                                    )
                                return None

                # Execute the command
                return await func(*args, **kwargs)

            except ValidationError as e:
                # Handle validation errors
                if ctx and hasattr(ctx, "respond"):
                    await ctx.respond(str(e))
                elif ctx and hasattr(ctx, "send"):
                    await ctx.send(str(e))
                else:
                    logging.error(
                        f"Validation failed but no response method available: {e}"
                    )
                return None

            except Exception as e:
                # Re-raise other exceptions
                raise

        return wrapper

    return decorator


def error_handler(error_types: tuple = (Exception,)):
    """
    Decorator to handle errors in commands.

    Args:
        error_types: Tuple of exception types to catch

    Usage:
        @error_handler((ValidationError, RateLimitError))
        async def my_command(self, ctx):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except error_types as e:
                # Get the context
                ctx = args[1] if len(args) > 1 else None

                if ctx:
                    # Format error message
                    if isinstance(e, JakeyBotError):
                        error_msg = str(e)
                    else:
                        error_msg = f"An error occurred: {str(e)}"

                    # Send error response
                    if hasattr(ctx, "respond"):
                        await ctx.respond(error_msg)
                    elif hasattr(ctx, "send"):
                        await ctx.send(error_msg)
                    else:
                        logging.error(
                            f"Error occurred but no response method available: {e}"
                        )

                # Log the error
                logging.error(f"Command error in {func.__name__}: {e}", exc_info=True)
                return None

        return wrapper

    return decorator


def require_permissions(*permissions):
    """
    Decorator to require specific Discord permissions.

    Args:
        *permissions: Discord permission names to require

    Usage:
        @require_permissions('manage_messages', 'ban_members')
        async def my_command(self, ctx):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = args[1] if len(args) > 1 else None

            if ctx and ctx.guild:
                # Check if user has required permissions
                member = ctx.guild.get_member(ctx.author.id)
                if member and not member.guild_permissions.administrator:
                    missing_permissions = [
                        perm
                        for perm in permissions
                        if not getattr(member.guild_permissions, perm, False)
                    ]

                    if missing_permissions:
                        from core.exceptions import PermissionError

                        raise PermissionError(
                            f"You need the following permissions: {', '.join(missing_permissions)}",
                            required_permissions=list(permissions),
                        )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def cooldown(rate: int, per: int, type: commands.BucketType = commands.BucketType.user):
    """
    Decorator to apply Discord.py cooldown with rate limiting.

    Args:
        rate: Number of commands allowed
        per: Time period in seconds
        type: Bucket type for cooldown

    Usage:
        @cooldown(3, 60)  # 3 commands per minute
        async def my_command(self, ctx):
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Apply Discord.py cooldown
        func = commands.cooldown(rate, per, type)(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except commands.CommandOnCooldown as e:
                ctx = args[1] if len(args) > 1 else None
                if ctx:
                    retry_after = int(e.retry_after)
                    await ctx.respond(
                        f"⏰ **Cooldown**: Try again in {retry_after} seconds."
                    )
                return None

        return wrapper

    return decorator


def _extract_field_value(obj: Any, field_path: str) -> Any:
    """
    Extract a value from an object using dot notation.

    Args:
        obj: Object to extract value from
        field_path: Path to the field (e.g., 'author.id')

    Returns:
        The field value or None if not found
    """
    try:
        for field in field_path.split("."):
            obj = getattr(obj, field)
        return obj
    except (AttributeError, TypeError):
        return None


# Convenience decorators
def secure_command(command_type: str = None, validation_rules: dict = None):
    """
    Combined decorator for secure commands with rate limiting and validation.

    Args:
        command_type: Type of command for rate limiting
        validation_rules: Input validation rules

    Usage:
        @secure_command('chat', {'content': lambda x: validate_message_content(x)})
        async def my_command(self, ctx, content):
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Apply rate limiting
        if command_type:
            func = rate_limit(command_type)(func)

        # Apply input validation
        if validation_rules:
            func = validate_input(validation_rules)(func)

        # Apply error handling
        func = error_handler((ValidationError, RateLimitError, JakeyBotError))(func)

        return func

    return decorator
