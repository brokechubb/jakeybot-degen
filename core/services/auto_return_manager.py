"""
Auto-Return Tool Manager for JakeyBot

This module manages automatic switching back to the default tool after a timeout.
It provides a way to temporarily use specific tools and then automatically return
to the Memory tool (or other default) for personalization.
"""

import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Tuple
from os import environ
import discord


class AutoReturnManager:
    """
    Manages automatic tool switching with timeout-based return to default.

    Features:
    - Automatic return to default tool after timeout
    - Tool-specific timeout configurations
    - User activity monitoring
    - Configurable default tool
    - Smart suggestions for tool usage
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.default_tool = environ.get("DEFAULT_TOOL", "Memory")
        self.tool_timeouts = self._get_tool_timeouts()
        self.active_timers: Dict[int, asyncio.Task] = {}
        self.user_tool_switches: Dict[int, Dict] = {}
        self.user_activity: Dict[int, Dict] = {}
        self.suggestion_cooldowns: Dict[int, datetime] = {}

        logging.info(
            f"AutoReturnManager initialized with default tool: {self.default_tool}"
        )

    def _get_tool_timeouts(self) -> Dict[str, int]:
        """Get tool-specific timeout configurations from environment variables."""
        timeouts = {
            "ExaSearch": int(environ.get("TOOL_TIMEOUT_EXASEARCH", "180")),  # 3 minutes
            "GitHub": int(environ.get("TOOL_TIMEOUT_GITHUB", "240")),  # 4 minutes
            "CodeExecution": int(
                environ.get("TOOL_TIMEOUT_CODEEXECUTION", "600")
            ),  # 10 minutes
            "AudioTools": int(
                environ.get("TOOL_TIMEOUT_AUDIOTOOLS", "300")
            ),  # 5 minutes
            "CryptoPrice": int(
                environ.get("TOOL_TIMEOUT_CRYPTOPRICE", "180")
            ),  # 3 minutes
            "CurrencyConverter": int(
                environ.get("TOOL_TIMEOUT_CURRENCYCONVERTER", "180")
            ),  # 3 minutes
            "YouTube": int(environ.get("TOOL_TIMEOUT_YOUTUBE", "240")),  # 4 minutes
            "IdeationTools": int(
                environ.get("TOOL_TIMEOUT_IDEATIONTOOLS", "300")
            ),  # 5 minutes
            "default": int(
                environ.get("TOOL_TIMEOUT_DEFAULT", "300")
            ),  # 5 minutes default
        }
        return timeouts

    async def switch_tool_with_timeout(
        self, guild_id: int, new_tool: str, user_id: Optional[int] = None
    ) -> None:
        """
        Switch to a new tool and schedule automatic return to default.

        Args:
            guild_id: The guild or user ID
            new_tool: The tool to switch to
            user_id: Optional user ID for user-specific tracking
        """
        try:
            # Cancel any existing timer for this guild/user
            await self.cancel_timer(guild_id)

            # Store the tool switch information
            self.user_tool_switches[guild_id] = {
                "tool": new_tool,
                "switched_at": datetime.now(timezone.utc),
                "user_id": user_id,
            }

            # Initialize user activity tracking
            self.user_activity[guild_id] = {
                "message_count": 0,
                "last_activity": datetime.now(timezone.utc),
                "tool_usage_patterns": [],
            }

            # Get the timeout for this tool
            timeout = self.tool_timeouts.get(new_tool, self.tool_timeouts["default"])

            # Schedule the auto-return
            timer_task = asyncio.create_task(
                self._auto_return_after_timeout(guild_id, timeout)
            )
            self.active_timers[guild_id] = timer_task

            logging.info(
                f"Switched guild {guild_id} to {new_tool} with {timeout}s timeout"
            )

        except Exception as e:
            logging.error(f"Error switching tool with timeout: {e}")
            raise

    async def record_user_activity(
        self, guild_id: int, message_content: str
    ) -> Optional[str]:
        """
        Record user activity and generate smart suggestions.

        Args:
            guild_id: The guild or user ID
            message_content: The content of the user's message

        Returns:
            Optional suggestion string if a suggestion should be made
        """
        if guild_id not in self.user_activity:
            return None

        # Update activity tracking
        self.user_activity[guild_id]["message_count"] += 1
        self.user_activity[guild_id]["last_activity"] = datetime.now(timezone.utc)

        # Check if we should make a suggestion (avoid spam)
        if not self._should_make_suggestion(guild_id):
            return None

        # Generate smart suggestions based on message content and activity
        suggestion = self._generate_smart_suggestion(guild_id, message_content)

        if suggestion:
            # Set cooldown to avoid spam
            self.suggestion_cooldowns[guild_id] = datetime.now(timezone.utc)
            return suggestion

        return None

    def _should_make_suggestion(self, guild_id: int) -> bool:
        """Check if we should make a suggestion (avoid spam)."""
        if guild_id not in self.suggestion_cooldowns:
            return True

        cooldown = self.suggestion_cooldowns[guild_id]
        time_since_last = (datetime.now(timezone.utc) - cooldown).total_seconds()

        # Minimum 2 minutes between suggestions
        return time_since_last > 120

    def _generate_smart_suggestion(
        self, guild_id: int, message_content: str
    ) -> Optional[str]:
        """
        Generate smart suggestions based on message content and user activity.

        Args:
            guild_id: The guild or user ID
            message_content: The content of the user's message

        Returns:
            Optional suggestion string
        """
        if guild_id not in self.user_tool_switches:
            return None

        current_tool = self.user_tool_switches[guild_id]["tool"]
        remaining_time = self._calculate_remaining_time(guild_id)
        message_count = self.user_activity[guild_id]["message_count"]

        # Suggestion 1: Low time remaining
        if remaining_time and remaining_time < 60:  # Less than 1 minute
            return f"⏰ **Time Alert**: You have less than 1 minute left with {current_tool}. Use `/extend_timeout <time>` to add more time, or `/return_to_default` to switch back now."

        # Suggestion 2: High activity (user is actively using the tool)
        if (
            message_count >= 5 and remaining_time and remaining_time < 120
        ):  # Less than 2 minutes
            return f"🔄 **Active Session**: You're actively using {current_tool} with {remaining_time // 60}m {remaining_time % 60}s remaining. Consider extending your session with `/extend_timeout 5m`."

        # Suggestion 3: Tool-specific suggestions based on content
        tool_suggestion = self._get_tool_specific_suggestion(
            current_tool, message_content, remaining_time
        )
        if tool_suggestion:
            return tool_suggestion

        # Suggestion 4: General timeout reminder
        if remaining_time and remaining_time < 180:  # Less than 3 minutes
            return f"⏰ **Reminder**: {current_tool} will return to {self.default_tool} in {remaining_time // 60}m {remaining_time % 60}s. Use `/timeout_status` to check remaining time."

        return None

    def _get_tool_specific_suggestion(
        self, current_tool: str, message_content: str, remaining_time: Optional[int]
    ) -> Optional[str]:
        """
        Generate tool-specific suggestions based on content and remaining time.

        Args:
            current_tool: The currently active tool
            message_content: The user's message content
            remaining_time: Remaining time in seconds

        Returns:
            Optional tool-specific suggestion
        """
        content_lower = message_content.lower()

        # ExaSearch suggestions
        if current_tool == "ExaSearch":
            if "search" in content_lower or "find" in content_lower:
                if remaining_time and remaining_time < 60:
                    return f"🔍 **Web Search**: Quick searches with {remaining_time}s remaining. Use `/extend_timeout 2m` for more searches, or `/return_to_default` to go back to Memory."

        # GitHub suggestions
        elif current_tool == "GitHub":
            if (
                "repo" in content_lower
                or "code" in content_lower
                or "file" in content_lower
            ):
                if remaining_time and remaining_time < 120:
                    return f"📚 **GitHub Work**: Working with repositories takes time! You have {remaining_time // 60}m {remaining_time % 60}s remaining. Extend with `/extend_timeout 5m`."

        # CodeExecution suggestions
        elif current_tool == "CodeExecution":
            if (
                "code" in content_lower
                or "run" in content_lower
                or "execute" in content_lower
            ):
                if remaining_time and remaining_time < 300:  # Less than 5 minutes
                    return f"💻 **Coding Session**: Coding takes time! You have {remaining_time // 60}m {remaining_time % 60}s remaining. Extend with `/extend_timeout 10m` for longer coding sessions."

        # AudioTools suggestions
        elif current_tool == "AudioTools":
            if (
                "audio" in content_lower
                or "voice" in content_lower
                or "sound" in content_lower
            ):
                if remaining_time and remaining_time < 120:
                    return f"🎵 **Audio Work**: Audio processing takes time! You have {remaining_time // 60}m {remaining_time % 60}s remaining. Extend with `/extend_timeout 5m` for more audio work."

        # YouTube suggestions
        elif current_tool == "YouTube":
            if (
                "video" in content_lower
                or "youtube" in content_lower
                or "summarize" in content_lower
            ):
                if remaining_time and remaining_time < 120:
                    return f"📺 **Video Analysis**: Video analysis takes time! You have {remaining_time // 60}m {remaining_time % 60}s remaining. Extend with `/extend_timeout 5m` for more video work."

        return None

    def _calculate_remaining_time(self, guild_id: int) -> Optional[int]:
        """Calculate remaining time for a guild/user (internal method)."""
        if guild_id not in self.user_tool_switches:
            return None

        switch_info = self.user_tool_switches[guild_id]
        tool = switch_info["tool"]
        switched_at = switch_info["switched_at"]
        timeout = self.tool_timeouts.get(tool, self.tool_timeouts["default"])

        elapsed = (datetime.now(timezone.utc) - switched_at).total_seconds()
        remaining = max(0, timeout - elapsed)

        return int(remaining)

    async def get_smart_suggestions(
        self, guild_id: int, message_content: str
    ) -> List[str]:
        """
        Get a list of smart suggestions for a user.

        Args:
            guild_id: The guild or user ID
            message_content: The content of the user's message

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Get activity-based suggestion
        activity_suggestion = await self.record_user_activity(guild_id, message_content)
        if activity_suggestion:
            suggestions.append(activity_suggestion)

        # Get timeout-based suggestions
        timeout_suggestions = self._get_timeout_suggestions(guild_id)
        suggestions.extend(timeout_suggestions)

        # Get tool-optimization suggestions
        optimization_suggestions = self._get_optimization_suggestions(
            guild_id, message_content
        )
        suggestions.extend(optimization_suggestions)

        return suggestions

    def _get_timeout_suggestions(self, guild_id: int) -> List[str]:
        """Get timeout-related suggestions."""
        suggestions = []

        if guild_id not in self.user_tool_switches:
            return suggestions

        current_tool = self.user_tool_switches[guild_id]["tool"]
        remaining_time = self._calculate_remaining_time(guild_id)

        if remaining_time is None:
            return suggestions

        # Critical time warning
        if remaining_time < 30:
            suggestions.append(
                f"🚨 **Critical**: {current_tool} will return to {self.default_tool} in {remaining_time} seconds! Use `/extend_timeout 5m` now!"
            )

        # Low time warning
        elif remaining_time < 60:
            suggestions.append(
                f"⚠️ **Warning**: {current_tool} will return to {self.default_tool} in {remaining_time} seconds."
            )

        # Moderate time reminder
        elif remaining_time < 180:
            suggestions.append(
                f"⏰ **Reminder**: {current_tool} will return to {self.default_tool} in {remaining_time // 60}m {remaining_time % 60}s."
            )

        return suggestions

    def _get_optimization_suggestions(
        self, guild_id: int, message_content: str
    ) -> List[str]:
        """Get tool optimization suggestions."""
        suggestions = []

        if guild_id not in self.user_tool_switches:
            return suggestions

        current_tool = self.user_tool_switches[guild_id]["tool"]
        content_lower = message_content.lower()

        # Tool-specific optimization tips
        if current_tool == "ExaSearch":
            if len(content_lower.split()) < 3:
                suggestions.append(
                    "💡 **Tip**: More specific searches get better results. Try: 'latest news about AI developments in 2025'"
                )

        elif current_tool == "CodeExecution":
            if "error" in content_lower or "bug" in content_lower:
                suggestions.append(
                    "💡 **Tip**: When debugging code, try to isolate the problem and test small parts first."
                )

        return suggestions

    async def cancel_timer(self, guild_id: int) -> None:
        """Cancel the auto-return timer for a specific guild/user."""
        if guild_id in self.active_timers:
            timer_task = self.active_timers[guild_id]
            if not timer_task.done():
                timer_task.cancel()
                try:
                    await timer_task
                except asyncio.CancelledError:
                    pass

            del self.active_timers[guild_id]

            if guild_id in self.user_tool_switches:
                del self.user_tool_switches[guild_id]

            if guild_id in self.user_activity:
                del self.user_activity[guild_id]

            logging.info(f"Cancelled auto-return timer for guild {guild_id}")

    async def extend_timeout(self, guild_id: int, additional_seconds: int) -> None:
        """
        Extend the current tool timeout.

        Args:
            guild_id: The guild or user ID
            additional_seconds: Additional seconds to add to the timeout
        """
        if guild_id not in self.active_timers:
            return

        # Cancel current timer
        await self.cancel_timer(guild_id)

        # Get current tool and remaining time
        if guild_id in self.user_tool_switches:
            current_tool = self.user_tool_switches[guild_id]["tool"]
            timeout = self.tool_timeouts.get(
                current_tool, self.tool_timeouts["default"]
            )

            # Create new timer with extended timeout
            timer_task = asyncio.create_task(
                self._auto_return_after_timeout(guild_id, timeout + additional_seconds)
            )
            self.active_timers[guild_id] = timer_task

            logging.info(
                f"Extended timeout for guild {guild_id} by {additional_seconds}s"
            )

    async def get_remaining_time(self, guild_id: int) -> Optional[int]:
        """Get the remaining time before auto-return for a guild/user."""
        return self._calculate_remaining_time(guild_id)

    async def get_current_tool(self, guild_id: int) -> Optional[str]:
        """Get the currently active tool for a guild/user."""
        if guild_id in self.user_tool_switches:
            return self.user_tool_switches[guild_id]["tool"]
        return None

    async def _auto_return_after_timeout(self, guild_id: int, timeout: int) -> None:
        """
        Internal method to handle the automatic return after timeout.

        Args:
            guild_id: The guild or user ID
            timeout: The timeout in seconds
        """
        try:
            # Wait for the timeout
            await asyncio.sleep(timeout)

            # Check if the timer was cancelled
            if guild_id not in self.active_timers:
                return

            # Perform the auto-return
            await self._perform_auto_return(guild_id)

        except asyncio.CancelledError:
            logging.info(f"Auto-return timer cancelled for guild {guild_id}")
        except Exception as e:
            logging.error(f"Error in auto-return timer for guild {guild_id}: {e}")

    async def _perform_auto_return(self, guild_id: int) -> None:
        """
        Perform the actual auto-return to the default tool.

        Args:
            guild_id: The guild or user ID
        """
        try:
            # Get the database connection from the bot
            if hasattr(self.bot, "DBConn") and self.bot.DBConn is not None:
                db_conn = self.bot.DBConn

                # Switch back to default tool
                await db_conn.set_tool_config(guild_id=guild_id, tool=self.default_tool)

                # Clear the timer and switch info
                if guild_id in self.active_timers:
                    del self.active_timers[guild_id]
                if guild_id in self.user_tool_switches:
                    del self.user_tool_switches[guild_id]
                if guild_id in self.user_activity:
                    del self.user_activity[guild_id]

                logging.info(f"Auto-returned guild {guild_id} to {self.default_tool}")

                # Try to notify the user (if we can find a channel)
                await self._notify_auto_return(guild_id)

            else:
                logging.error("Database connection not available for auto-return")

        except Exception as e:
            logging.error(f"Error performing auto-return for guild {guild_id}: {e}")

    async def _notify_auto_return(self, guild_id: int) -> None:
        """
        Try to notify the user about the auto-return.

        Args:
            guild_id: The guild or user ID
        """
        try:
            # Try to find a channel to send the notification
            if hasattr(self.bot, "DBConn") and self.bot.DBConn is not None:
                # Get the last channel used by this guild/user
                # This is a simplified approach - you might want to store the channel ID
                # when the tool is switched
                pass

            # For now, we'll just log the auto-return
            logging.info(f"Auto-return notification would be sent for guild {guild_id}")

        except Exception as e:
            logging.error(f"Error sending auto-return notification: {e}")

    async def cleanup(self) -> None:
        """Clean up all active timers when shutting down."""
        for guild_id in list(self.active_timers.keys()):
            await self.cancel_timer(guild_id)

        logging.info("AutoReturnManager cleanup completed")

    def get_status(self) -> Dict:
        """Get the current status of the auto-return manager."""
        return {
            "default_tool": self.default_tool,
            "active_timers": len(self.active_timers),
            "tool_timeouts": self.tool_timeouts,
            "active_switches": len(self.user_tool_switches),
            "active_users": len(self.user_activity),
        }
