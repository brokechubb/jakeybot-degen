"""
Auto-Return Tool Manager for JakeyBot

This module manages automatic switching back to the default tool after a timeout.
It provides a way to temporarily use specific tools and then automatically return
to the Memory tool (or other default) for personalization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
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
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.default_tool = environ.get("DEFAULT_TOOL", "Memory")
        self.tool_timeouts = self._get_tool_timeouts()
        self.active_timers: Dict[int, asyncio.Task] = {}
        self.user_tool_switches: Dict[int, Dict] = {}
        
        logging.info(f"AutoReturnManager initialized with default tool: {self.default_tool}")
    
    def _get_tool_timeouts(self) -> Dict[str, int]:
        """Get tool-specific timeout configurations from environment variables."""
        timeouts = {
            "ImageGen": int(environ.get("TOOL_TIMEOUT_IMAGEGEN", "300")),      # 5 minutes
            "ExaSearch": int(environ.get("TOOL_TIMEOUT_EXASEARCH", "180")),    # 3 minutes
            "GitHub": int(environ.get("TOOL_TIMEOUT_GITHUB", "240")),          # 4 minutes
            "CodeExecution": int(environ.get("TOOL_TIMEOUT_CODEEXECUTION", "600")), # 10 minutes
            "AudioTools": int(environ.get("TOOL_TIMEOUT_AUDIOTOOLS", "300")),  # 5 minutes
            "CryptoPrice": int(environ.get("TOOL_TIMEOUT_CRYPTOPRICE", "180")), # 3 minutes
            "CurrencyConverter": int(environ.get("TOOL_TIMEOUT_CURRENCYCONVERTER", "180")), # 3 minutes
            "YouTube": int(environ.get("TOOL_TIMEOUT_YOUTUBE", "240")),        # 4 minutes
            "IdeationTools": int(environ.get("TOOL_TIMEOUT_IDEATIONTOOLS", "300")), # 5 minutes
            "default": int(environ.get("TOOL_TIMEOUT_DEFAULT", "300"))          # 5 minutes default
        }
        return timeouts
    
    async def switch_tool_with_timeout(self, guild_id: int, new_tool: str, user_id: Optional[int] = None) -> None:
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
                "switched_at": datetime.utcnow(),
                "user_id": user_id
            }
            
            # Get the timeout for this tool
            timeout = self.tool_timeouts.get(new_tool, self.tool_timeouts["default"])
            
            # Schedule the auto-return
            timer_task = asyncio.create_task(self._auto_return_after_timeout(guild_id, timeout))
            self.active_timers[guild_id] = timer_task
            
            logging.info(f"Switched guild {guild_id} to {new_tool} with {timeout}s timeout")
            
        except Exception as e:
            logging.error(f"Error switching tool with timeout: {e}")
            raise
    
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
            timeout = self.tool_timeouts.get(current_tool, self.tool_timeouts["default"])
            
            # Create new timer with extended timeout
            timer_task = asyncio.create_task(self._auto_return_after_timeout(guild_id, timeout + additional_seconds))
            self.active_timers[guild_id] = timer_task
            
            logging.info(f"Extended timeout for guild {guild_id} by {additional_seconds}s")
    
    async def get_remaining_time(self, guild_id: int) -> Optional[int]:
        """Get the remaining time before auto-return for a guild/user."""
        if guild_id not in self.user_tool_switches:
            return None
        
        switch_info = self.user_tool_switches[guild_id]
        tool = switch_info["tool"]
        switched_at = switch_info["switched_at"]
        timeout = self.tool_timeouts.get(tool, self.tool_timeouts["default"])
        
        elapsed = (datetime.utcnow() - switched_at).total_seconds()
        remaining = max(0, timeout - elapsed)
        
        return int(remaining)
    
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
            "active_switches": len(self.user_tool_switches)
        }
