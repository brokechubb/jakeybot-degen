import logging
import discord
from discord.ext import commands
from discord import Member, DiscordException
import yaml
import os
from datetime import datetime, timedelta, timezone
from core.services.helperfunctions import HelperFunctions
from core.ai.history import History
import motor.motor_asyncio
from os import environ
import google.generativeai as genai
from google.generativeai import types
import aiohttp
import io
import requests
import time
import asyncio
import re


class Misc(commands.Cog):
    """Use my other utilities here that can help make your server more active and entertaining"""

    def __init__(self, bot):
        self.bot = bot
        self.author = environ.get("BOT_NAME", "Jakey Bot")

        # Use the shared database connection from the bot
        if hasattr(bot, "DBConn") and bot.DBConn is not None:
            self.DBConn = bot.DBConn
            logging.info("Misc cog using shared database connection")
        else:
            # Fallback: create our own connection if shared one is not available
            try:
                self.DBConn: History = History(
                    bot=bot,
                    db_conn=motor.motor_asyncio.AsyncIOMotorClient(
                        environ.get("MONGO_DB_URL")
                    ),
                )
                logging.info("Misc cog created fallback database connection")
            except Exception as e:
                logging.error(
                    f"Failed to initialize database connection in Misc cog: {e}"
                )
                self.DBConn = None

        # Only start reminder checker if we have a database connection
        if self.DBConn:
            self.bot.loop.create_task(self._check_reminders())
            logging.info("Reminder checker started")
        else:
            logging.warning("Reminder checker not started - no database connection")

        # Check if Gemini API is configured
        self._gemini_api_configured = False
        if hasattr(bot, "_gemini_api_configured") and bot._gemini_api_configured:
            self._gemini_api_configured = True
            logging.info("Misc cog detected globally configured Gemini API.")
        else:
            # Try to configure locally
            api_key = environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self._gemini_api_configured = True
                    logging.info("Misc cog configured Gemini API locally.")
                except Exception as e:
                    logging.warning(f"Failed to configure Gemini API locally: {e}")

        # Initialize auto-image settings and load from database
        self._auto_image_enabled = {}
        if self.DBConn:
            self.bot.loop.create_task(self._load_auto_image_settings())
            logging.info("Auto-image settings loader started")
        else:
            logging.warning(
                "Auto-image settings loader not started - no database connection"
            )

    async def _check_reminders(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                guild_id = guild.id
                due_reminders = await self.DBConn.get_due_reminders(guild_id)
                for reminder in due_reminders:
                    channel = self.bot.get_channel(reminder["channel_id"])
                    if channel:
                        await channel.send(
                            f"⏰ Reminder for <@{reminder['user_id']}>: {reminder['message']}"
                        )
                    await self.DBConn.delete_reminder(guild_id, reminder["_id"])
            await asyncio.sleep(60)  # Check every minute

    @commands.slash_command(
        name="remind",
        description="Set a reminder for yourself.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "time_in",
        description="When to remind you (e.g., '1h', '30m', 'tomorrow 10am')",
        required=True,
    )
    @discord.option("message", description="What to remind you about", required=True)
    async def remind_me(self, ctx, time_in: str, message: str):
        """Set a reminder for yourself."""
        await ctx.response.defer(ephemeral=True)

        try:
            remind_time = self._parse_time_input(time_in)
            if remind_time is None:
                await ctx.respond(
                    "⚠️ Invalid time format. Please use formats like '1h', '30m', 'tomorrow 10am'."
                )
                return

            if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
                guild_id = ctx.guild.id if ctx.guild else ctx.author.id
            else:
                guild_id = ctx.author.id

            reminder_id = await self.DBConn.add_reminder(
                guild_id=guild_id,
                user_id=ctx.author.id,
                channel_id=ctx.channel.id,
                message=message,
                remind_time=remind_time,
            )
            await ctx.respond(
                f"✅ I'll remind you about '{message}' at {remind_time.strftime('%Y-%m-%d %H:%M:%S')}."
            )
        except Exception as e:
            await ctx.respond(f"❌ Failed to set reminder: {str(e)}")
            logging.error("Error setting reminder: %s", e)

    def _parse_time_input(self, time_input: str) -> datetime:
        now = datetime.now()
        time_input = time_input.lower()

        if time_input.endswith("m"):
            minutes = int(time_input[:-1])
            return now + timedelta(minutes=minutes)
        elif time_input.endswith("h"):
            hours = int(time_input[:-1])
            return now + timedelta(hours=hours)
        elif time_input.endswith("d"):
            days = int(time_input[:-1])
            return now + timedelta(days=days)
        elif "tomorrow" in time_input:
            tomorrow = now + timedelta(days=1)
            if " " in time_input:
                time_part = time_input.split(" ", 1)[1]
                try:
                    hour = int(time_part.replace("am", "").replace("pm", "").strip())
                    if "pm" in time_part and hour < 12:
                        hour += 12
                    elif "am" in time_part and hour == 12:  # 12am is midnight
                        hour = 0
                    return tomorrow.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                except ValueError:
                    pass  # Fall through to default if time part is invalid
            return tomorrow.replace(
                hour=9, minute=0, second=0, microsecond=0
            )  # Default to 9am tomorrow

        # Basic parsing for specific time (e.g., "10am", "2pm")
        match = re.match(r"(\d+)(am|pm)", time_input)
        if match:
            hour = int(match.group(1))
            ampm = match.group(2)
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:  # 12am is midnight
                hour = 0

            # If the target time is already past today, set for tomorrow
            target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if target_time <= now:
                target_time += timedelta(days=1)
            return target_time

        return None

    @commands.slash_command(
        name="auto_image",
        description="Toggle automatic image generation for simple requests",
    )
    @commands.has_permissions(manage_channels=True)
    async def auto_image(self, ctx, enabled: bool = None):
        """Toggle automatic image generation mode."""
        guild_id = str(ctx.guild.id)

        # Get current setting
        current_setting = self._auto_image_enabled.get(guild_id, False)

        if enabled is None:
            # Toggle the current setting
            enabled = not current_setting

        # Update the setting in memory
        self._auto_image_enabled[guild_id] = enabled

        # Save the setting to the database
        save_success = await self._save_auto_image_setting(guild_id, enabled)

        if save_success:
            if enabled:
                await ctx.respond(
                    "🎨 **Auto-Image Generation Enabled!**\n"
                    "Jakey will now automatically generate images for simple requests.\n"
                    "Users can still use manual commands for more control.\n"
                    "✅ Setting saved to database (persistent across restarts).",
                    ephemeral=True,
                )
            else:
                await ctx.respond(
                    "🎨 **Auto-Image Generation Disabled!**\n"
                    "Jakey will only suggest image generation commands.\n"
                    "Users must manually use `/generate_image` or `/edit_image`.\n"
                    "✅ Setting saved to database (persistent across restarts).",
                    ephemeral=True,
                )
        else:
            # If saving failed, revert the memory setting
            self._auto_image_enabled[guild_id] = current_setting
            await ctx.respond(
                "❌ **Failed to save setting!**\n"
                "The change was not saved to the database.\n"
                "Please try again or contact an administrator.",
                ephemeral=True,
            )

    async def _auto_generate_image(self, message, prompt: str):
        """Automatically generate an image for a user request."""
        if not self._gemini_api_configured:
            return False

        try:
            # Send initial status message
            status_msg = await message.channel.send(
                f"🎨 **Auto-Generating Image**\n"
                f"Prompt: *{prompt}*\n"
                f"⌛ This may take a few minutes...",
                reference=message,
            )

            # Get the model for image generation - use a model that supports image generation
            model_name = environ.get("DEFAULT_GEMINI_IMAGE_GENERATION_MODEL", "gemini-2.0-flash-preview-image-generation")
            if not model_name or model_name == "gemini-model-id":
                model_name = "gemini-2.0-flash-preview-image-generation"  # Fallback to a model that supports image generation
            
            logging.info(f"Using auto-image generation model: {model_name}")
            model = genai.GenerativeModel(model_name=model_name)

                        # Generate the image with safety settings disabled
            response = await model.generate_content_async(
                contents=prompt,
                generation_config={
                    "temperature": 0.7,  # Default temperature for auto-generation
                    "max_output_tokens": 8192,
                    "response_modalities": ["IMAGE"]
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )

            if not response.candidates or not response.candidates[0].content:
                await status_msg.edit(
                    content="❌ Auto-generation failed. Please try `/generate_image` manually."
                )
                return False

            # Check for safety issues
            if response.candidates[0].finish_reason == "IMAGE_SAFETY":
                await status_msg.edit(
                    content="❌ Auto-generation blocked by safety filters. Please try a different prompt."
                )
                return False

            # Process and send generated images
            images_sent = 0
            for index, part in enumerate(response.candidates[0].content.parts):
                if hasattr(part, "inline_data") and part.inline_data:
                    # Create filename with timestamp
                    timestamp = datetime.now().strftime("%H_%M_%S_%m%d%Y_%s")
                    filename = f"auto_generated_{timestamp}_part{index}.png"

                    # Send the image
                    file = discord.File(
                        fp=io.BytesIO(part.inline_data.data), filename=filename
                    )

                    await message.channel.send(
                        f"🎨 **Auto-Generated Image {index + 1}**\n"
                        f"Prompt: *{prompt}*\n"
                        f"💡 Use `/generate_image` for more control next time!",
                        file=file,
                        reference=message,
                    )
                    images_sent += 1

            if images_sent > 0:
                await status_msg.edit(
                    content=f"✅ **Auto-Generation Complete!** Generated {images_sent} image(s)."
                )
                return True
            else:
                await status_msg.edit(
                    content="❌ No images were generated. Please try `/generate_image` manually."
                )
                return False

        except Exception as e:
            logging.error(f"Error in auto-image generation: {e}")
            await status_msg.edit(content=f"❌ Auto-generation error: {str(e)[:100]}")
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and automatically offer image generation when appropriate."""
        # Ignore bot messages and commands
        if message.author.bot or message.content.startswith("/"):
            return

        # Check if the message is asking for image generation
        image_keywords = [
            "generate an image",
            "create an image",
            "make an image",
            "draw me",
            "show me a picture",
            "generate a picture",
            "create a picture",
            "make a picture",
            "draw a",
            "show a",
            "can you draw",
            "can you create",
            "can you make",
            "can you generate",
            "i want an image",
            "i need an image",
            "i'd like an image",
            "i would like an image",
            "generate image of",
            "create image of",
            "make image of",
            "draw image of",
            "picture of",
            "image of",
            "drawing of",
            "art of",
            "illustration of",
        ]

        message_lower = message.content.lower()
        is_image_request = any(keyword in message_lower for keyword in image_keywords)

        if is_image_request:
            # Extract potential prompt from the message
            prompt = self._extract_image_prompt(message.content)

            # Check if auto-generation is enabled for this guild
            guild_id = str(message.guild.id) if message.guild else "dm"
            auto_enabled = getattr(self, "_auto_image_enabled", {}).get(guild_id, False)

            if (
                auto_enabled and len(prompt) > 10
            ):  # Only auto-generate for substantial prompts
                # Try to auto-generate the image
                success = await self._auto_generate_image(message, prompt)
                if success:
                    return  # Don't send the suggestion if auto-generation succeeded

            # Create a helpful response with image generation options
            embed = discord.Embed(
                title="🎨 Image Generation Detected!",
                description=f"I detected you're asking for an image! Here are your options:",
                color=0x00FF00,
            )

            embed.add_field(
                name="🖼️ Generate New Image",
                value=f"Use `/generate_image {prompt}` to create a new image",
                inline=False,
            )

            embed.add_field(
                name="✏️ Edit Existing Image",
                value="Attach an image and use `/edit_image <prompt>` to modify it",
                inline=False,
            )

            embed.add_field(
                name="❓ Need Help?",
                value="Use `/image_help` for detailed instructions",
                inline=False,
            )

            embed.set_footer(
                text="💡 Tip: You can also adjust creativity with the temperature parameter"
            )

            # Send the helpful response
            await message.channel.send(embed=embed, reference=message)

    def _extract_image_prompt(self, message_content: str) -> str:
        """Extract a potential image prompt from a message."""
        # Remove common request words to get to the actual description
        request_words = [
            "generate an image of",
            "create an image of",
            "make an image of",
            "draw me",
            "generate a picture of",
            "create a picture of",
            "make a picture of",
            "can you draw",
            "can you create",
            "can you make",
            "can you generate",
            "i want an image of",
            "i need an image of",
            "i'd like an image of",
            "i would like an image of",
            "show me a picture of",
            "show a picture of",
            "picture of",
            "image of",
            "drawing of",
            "art of",
            "illustration of",
        ]

        message_lower = message_content.lower()
        prompt = message_content

        # Try to extract the actual description
        for request_word in request_words:
            if request_word in message_lower:
                # Find the position after the request word
                start_pos = message_lower.find(request_word) + len(request_word)
                prompt = message_content[start_pos:].strip()
                break

        # Clean up the prompt
        prompt = prompt.strip(".,!?")

        # If prompt is too short, provide a default
        if len(prompt) < 3:
            prompt = "your request"

        return prompt

    @commands.slash_command(
        name="time",
        description="Displays the current time and DST status.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def current_time_slash(self, ctx):
        """Displays the current time and DST status."""
        now = datetime.now()
        dst_status = "active" if time.localtime().tm_isdst else "inactive"
        await ctx.respond(
            f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}. Daylight Saving Time is currently {dst_status}."
        )

    @commands.command(
        name="time", description="Displays the current time and DST status."
    )
    async def current_time_prefix(self, ctx):
        """Displays the current time and DST status."""
        now = datetime.now()
        dst_status = "active" if time.localtime().tm_isdst else "inactive"
        await ctx.send(
            f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}. Daylight Saving Time is currently {dst_status}."
        )

    @commands.slash_command(
        name="memory_debug",
        description="Debug the memory system and check its status.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def memory_debug(self, ctx):
        """Debug the memory system and check its status."""
        await ctx.response.defer(ephemeral=True)

        if not self.DBConn:
            await ctx.respond("❌ Database connection not available")
            return

        try:
            # Determine guild/user ID
            if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
                guild_id = ctx.guild.id if ctx.guild else ctx.author.id
            else:
                guild_id = ctx.author.id

            # Check memory status
            status = await self.DBConn.check_memory_status(guild_id)

            # Create embed with debug information
            embed = discord.Embed(
                title="🧠 Memory System Debug",
                color=discord.Color.blue()
                if status["status"] == "ok"
                else discord.Color.red(),
            )

            embed.add_field(name="Status", value=status["status"].upper(), inline=True)

            embed.add_field(name="Message", value=status["message"], inline=True)

            if status["status"] == "ok":
                embed.add_field(
                    name="Total Facts", value=str(status["total_facts"]), inline=True
                )

                embed.add_field(
                    name="Non-expired Facts",
                    value=str(status["non_expired_facts"]),
                    inline=True,
                )

                embed.add_field(
                    name="Text Index",
                    value="✅ Exists" if status["text_index_exists"] else "❌ Missing",
                    inline=True,
                )

                embed.add_field(
                    name="Collection", value=status["collection_name"], inline=False
                )

                if status["indexes"]:
                    embed.add_field(
                        name="Indexes", value=", ".join(status["indexes"]), inline=False
                    )

            # Add database connection info
            embed.add_field(
                name="Database",
                value=f"Connected: {'✅' if self.DBConn else '❌'}",
                inline=True,
            )

            embed.add_field(
                name="Shared Connection",
                value="✅" if hasattr(self.bot, "DBConn") and self.bot.DBConn else "❌",
                inline=True,
            )

            await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f"❌ Error during memory debug: {str(e)}")
            logging.error(f"Memory debug error: {e}")

    @commands.slash_command(
        name="memory_reindex",
        description="Force reindex the memory system to fix search issues.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def memory_reindex(self, ctx):
        """Force reindex the memory system to fix search issues."""
        await ctx.response.defer(ephemeral=True)

        if not self.DBConn:
            await ctx.respond("❌ Database connection not available")
            return

        try:
            # Determine guild/user ID
            if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
                guild_id = ctx.guild.id if ctx.guild else ctx.author.id
            else:
                guild_id = ctx.author.id

            # Force reindex
            success = await self.DBConn.force_reindex_memory(guild_id)

            if success:
                await ctx.respond(
                    "✅ Memory system reindexed successfully! Search should work better now."
                )
            else:
                await ctx.respond(
                    "❌ Failed to reindex memory system. Check logs for details."
                )

        except Exception as e:
            await ctx.respond(f"❌ Error during memory reindex: {str(e)}")
            logging.error(f"Memory reindex error: {e}")

    @commands.slash_command(
        contexts={discord.InteractionContextType.guild},
        integration_types={discord.IntegrationType.guild_install},
    )
    async def mimic(self, ctx, user: Member, message_body: str):
        """Mimic as user!"""
        await ctx.response.defer(ephemeral=True)

        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        avatar_url = (
            user.avatar.url
            if user.avatar
            else "https://cdn.discordapp.com/embed/avatars/0.png"
        )

        # Set display name depending on whether if the user joins in particular guild or in DMs to have different display names
        if ctx.guild:
            _xuser_display_name = await ctx.guild.fetch_member(user.id)
            user_name = f"{_xuser_display_name.display_name}"
        else:
            _xuser_display_name = await self.bot.fetch_user(user.id)
            user_name = f"{_xuser_display_name.display_name}"

        webhook = await ctx.channel.create_webhook(
            name=f"Mimic command by {self.author}"
        )

        if not message_body:
            await ctx.respond("⚠️ Please specify a message to mimic!")
            return
        await webhook.send(
            content=message_body, username=user_name, avatar_url=avatar_url
        )
        await webhook.delete()

        await ctx.respond("✅ Done!")

    @commands.slash_command(
        name="timeout_status",
        description="Check the remaining time before auto-return to default tool.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def timeout_status(self, ctx):
        """Check the remaining time before auto-return to default tool."""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if AutoReturnManager is available
        if (
            not hasattr(self.bot, "auto_return_manager")
            or not self.bot.auto_return_manager
        ):
            await ctx.respond("❌ Auto-return system is not available")
            return

        # Get current tool and remaining time
        current_tool = await self.bot.auto_return_manager.get_current_tool(guild_id)
        remaining_time = await self.bot.auto_return_manager.get_remaining_time(guild_id)

        if current_tool is None:
            await ctx.respond(
                "✅ Currently using default tool (no auto-return scheduled)"
            )
        else:
            # Format remaining time
            if remaining_time is not None:
                minutes = remaining_time // 60
                seconds = remaining_time % 60

                if minutes > 0:
                    time_str = (
                        f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
                    )
                else:
                    time_str = f"{seconds}s"

                await ctx.respond(
                    f"⏰ **Current Tool:** {current_tool}\n"
                    f"🕐 **Time Remaining:** {time_str}\n"
                    f"🧠 **Will Return To:** {self.bot.auto_return_manager.default_tool}"
                )
            else:
                await ctx.respond(
                    f"⏰ **Current Tool:** {current_tool}\n"
                    f"❓ **Time Remaining:** Unknown\n"
                    f"🧠 **Will Return To:** {self.bot.auto_return_manager.default_tool}"
                )

    @commands.slash_command(
        name="extend_timeout",
        description="Extend the current tool timeout by additional time.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "additional_time",
        description="Additional time to add (e.g., '5m', '2h', '30s')",
        required=True,
    )
    async def extend_timeout(self, ctx, additional_time: str):
        """Extend the current tool timeout by additional time."""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if AutoReturnManager is available
        if (
            not hasattr(self.bot, "auto_return_manager")
            or not self.bot.auto_return_manager
        ):
            await ctx.respond("❌ Auto-return system is not available")
            return

        # Parse additional time
        try:
            additional_seconds = self._parse_time_input(additional_time)
            if additional_seconds is None:
                await ctx.respond(
                    "⚠️ Invalid time format. Please use formats like '5m', '2h', '30s'"
                )
                return
        except Exception as e:
            await ctx.respond(f"⚠️ Error parsing time: {str(e)}")
            return

        # Check if there's an active tool
        current_tool = await self.bot.auto_return_manager.get_current_tool(guild_id)
        if current_tool is None:
            await ctx.respond("❌ No active tool timeout to extend")
            return

        # Extend the timeout
        try:
            await self.bot.auto_return_manager.extend_timeout(
                guild_id, additional_seconds
            )

            # Get new remaining time
            new_remaining_time = await self.bot.auto_return_manager.get_remaining_time(
                guild_id
            )

            if new_remaining_time is not None:
                minutes = new_remaining_time // 60
                seconds = new_remaining_time % 60

                if minutes > 0:
                    time_str = (
                        f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
                    )
                else:
                    time_str = f"{seconds}s"

                await ctx.respond(
                    f"⏰ **Timeout Extended!**\n"
                    f"🛠️ **Current Tool:** {current_tool}\n"
                    f"🕐 **New Time Remaining:** {time_str}\n"
                    f"🧠 **Will Return To:** {self.bot.auto_return_manager.default_tool}"
                )
            else:
                await ctx.respond(
                    f"⏰ **Timeout Extended!**\n"
                    f"🛠️ **Current Tool:** {current_tool}\n"
                    f"🕐 **New Time Remaining:** Unknown\n"
                    f"🧠 **Will Return To:** {self.bot.auto_return_manager.default_tool}"
                )

        except Exception as e:
            await ctx.respond(f"❌ Failed to extend timeout: {str(e)}")
            logging.error(f"Error extending timeout: {e}")

    @commands.slash_command(
        name="return_to_default",
        description="Immediately return to the default tool.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def return_to_default(self, ctx):
        """Immediately return to the default tool."""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if AutoReturnManager is available
        if (
            not hasattr(self.bot, "auto_return_manager")
            or not self.bot.auto_return_manager
        ):
            await ctx.respond("❌ Auto-return system is not available")
            return

        # Check if there's an active tool
        current_tool = await self.bot.auto_return_manager.get_current_tool(guild_id)
        if current_tool is None:
            await ctx.respond("✅ Already using default tool")
            return

        # Cancel the timer and return to default
        try:
            await self.bot.auto_return_manager.cancel_timer(guild_id)

            # Set the tool back to default in the database
            if hasattr(self.bot, "DBConn") and self.bot.DBConn is not None:
                await self.bot.DBConn.set_tool_config(
                    guild_id=guild_id, tool=self.bot.auto_return_manager.default_tool
                )

            await ctx.respond(
                f"🧠 **Returned to Default Tool!**\n"
                f"✅ Now using: {self.bot.auto_return_manager.default_tool}\n"
                f"⏰ Auto-return timer cancelled"
            )

        except Exception as e:
            await ctx.respond(f"❌ Failed to return to default: {str(e)}")
            logging.error(f"Error returning to default: {e}")

    @commands.slash_command(
        name="smart_suggestions",
        description="Get intelligent suggestions for tool usage and optimization.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def smart_suggestions(self, ctx):
        """Get intelligent suggestions for tool usage and optimization."""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if AutoReturnManager is available
        if (
            not hasattr(self.bot, "auto_return_manager")
            or not self.bot.auto_return_manager
        ):
            await ctx.respond("❌ Auto-return system is not available")
            return

        # Get smart suggestions based on current context
        suggestions = await self.bot.auto_return_manager.get_smart_suggestions(
            guild_id, "smart_suggestions_request"
        )

        if not suggestions:
            # Provide general helpful suggestions
            current_tool = await self.bot.auto_return_manager.get_current_tool(guild_id)

            if current_tool is None:
                await ctx.respond(
                    f"🧠 **Smart Suggestions**\n\n"
                    f"✅ **Current Status**: Using default tool ({self.bot.auto_return_manager.default_tool})\n\n"
                    f"💡 **General Tips**:\n"
                    f"• Use `/feature <tool>` to switch to specific tools\n"
                    f"• Tools automatically return to {self.bot.auto_return_manager.default_tool} after timeout\n"
                    f"• Use `/timeout_status` to check remaining time\n"
                    f"• Use `/extend_timeout <time>` to extend sessions\n"
                    f"• Use `/return_to_default` to return immediately"
                )
            else:
                remaining_time = await self.bot.auto_return_manager.get_remaining_time(
                    guild_id
                )
                if remaining_time is not None:
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60

                    if minutes > 0:
                        time_str = (
                            f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
                        )
                    else:
                        time_str = f"{seconds}s"

                    await ctx.respond(
                        f"🧠 **Smart Suggestions**\n\n"
                        f"🛠️ **Current Tool**: {current_tool}\n"
                        f"⏰ **Time Remaining**: {time_str}\n\n"
                        f"💡 **Suggestions**:\n"
                        f"• Use `/extend_timeout <time>` to add more time\n"
                        f"• Use `/return_to_default` to switch back now\n"
                        f"• Use `/timeout_status` for detailed status\n"
                        f"• Plan your workflow to maximize tool usage"
                    )
                else:
                    await ctx.respond(
                        f"🧠 **Smart Suggestions**\n\n"
                        f"🛠️ **Current Tool**: {current_tool}\n"
                        f"⏰ **Time Status**: Unknown\n\n"
                        f"💡 **Suggestions**:\n"
                        f"• Use `/timeout_status` to check remaining time\n"
                        f"• Use `/extend_timeout <time>` to add more time\n"
                        f"• Use `/return_to_default` to switch back now"
                    )
        else:
            # Format multiple suggestions
            suggestion_text = "\n\n".join(
                [f"💡 {suggestion}" for suggestion in suggestions]
            )

            await ctx.respond(
                f"🧠 **Smart Suggestions**\n\n{suggestion_text}\n\n"
                f"💡 **Quick Actions**:\n"
                f"• `/extend_timeout <time>` - Add more time\n"
                f"• `/return_to_default` - Switch back now\n"
                f"• `/timeout_status` - Check remaining time"
            )

    @commands.slash_command(
        name="auto_return_status",
        description="Check the status of the auto-return system.",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def auto_return_status(self, ctx):
        """Check the status of the auto-return system."""
        await ctx.response.defer(ephemeral=True)

        # Check if AutoReturnManager is available
        if (
            not hasattr(self.bot, "auto_return_manager")
            or not self.bot.auto_return_manager
        ):
            await ctx.respond("❌ Auto-return system is not available")
            return

        # Get system status
        status = self.bot.auto_return_manager.get_status()

        # Format timeouts for display
        timeout_info = []
        for tool, timeout in status["tool_timeouts"].items():
            if tool != "default":
                minutes = timeout // 60
                seconds = timeout % 60
                if minutes > 0:
                    time_str = (
                        f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
                    )
                else:
                    time_str = f"{seconds}s"
                timeout_info.append(f"• **{tool}**: {time_str}")

        timeout_info.sort()

        await ctx.respond(
            f"🧠 **Auto-Return System Status**\n\n"
            f"✅ **Default Tool:** {status['default_tool']}\n"
            f"⏰ **Active Timers:** {status['active_timers']}\n"
            f"🔄 **Active Switches:** {status['active_switches']}\n"
            f"👥 **Active Users:** {status['active_users']}\n\n"
            f"**Tool Timeouts:**\n" + "\n".join(timeout_info) + "\n"
            f"• **Default**: {status['tool_timeouts']['default'] // 60}m {status['tool_timeouts']['default'] % 60}s"
        )

    @commands.slash_command(
        name="generate_image", description="Generate an image using AI"
    )
    async def generate_image(self, ctx, prompt: str, temperature: float = 0.7):
        """Generate an image using Gemini AI without needing the AI to use tools."""
        if not self._gemini_api_configured:
            await ctx.respond(
                "❌ Image generation is not available. Please check the bot configuration.",
                ephemeral=True,
            )
            return

        # Check temperature limits
        if temperature < 0.0 or temperature > 1.2:
            await ctx.respond(
                "❌ Temperature must be between 0.0 and 1.2", ephemeral=True
            )
            return

        # Send initial status message
        status_msg = await ctx.respond(
            f"⌛ Generating image with prompt: **{prompt}**... This may take a few minutes."
        )

        try:
            # Get the model for image generation - use a model that supports image generation
            model_name = environ.get("DEFAULT_GEMINI_IMAGE_GENERATION_MODEL", "gemini-2.0-flash-preview-image-generation")
            if not model_name or model_name == "gemini-model-id":
                model_name = "gemini-2.0-flash-preview-image-generation"  # Fallback to a model that supports image generation
            
            logging.info(f"Using image generation model: {model_name}")
            model = genai.GenerativeModel(model_name=model_name)

            # Generate the image with safety settings disabled
            response = await model.generate_content_async(
                    contents=prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": 8192,
                        "response_modalities": ["IMAGE"]
                    },
                    safety_settings=[
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH", 
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE"
                        }
                    ]
                )

            if not response.candidates or not response.candidates[0].content:
                logging.warning(f"No candidates or content in response for prompt: {prompt}")
                await status_msg.edit(
                    content="❌ Failed to generate image. Please try again."
                )
                return
            
            # Log response structure for debugging
            logging.info(f"Response structure: candidates={len(response.candidates)}, content_parts={len(response.candidates[0].content.parts)}")
            logging.info(f"First candidate finish_reason: {response.candidates[0].finish_reason}")
            
            # Check if finish_reason indicates an error
            if response.candidates[0].finish_reason != "STOP":
                logging.warning(f"Generation may not have completed successfully. Finish reason: {response.candidates[0].finish_reason}")
                if response.candidates[0].finish_reason == 1:
                    logging.warning("Finish reason 1 typically indicates an error or incomplete generation")
            
            # Log the actual response content for debugging
            for i, part in enumerate(response.candidates[0].content.parts):
                logging.info(f"Response part {i}: {part}")
                if hasattr(part, 'text') and part.text:
                    logging.info(f"Part {i} text length: {len(part.text)}")
                    logging.info(f"Part {i} text preview: {part.text[:200]}...")

            # Check for safety issues
            if response.candidates[0].finish_reason == "IMAGE_SAFETY":
                await status_msg.edit(
                    content="❌ Image generation blocked by safety filters. Please try a different prompt."
                )
                return

            # Process and send generated images
            logging.info(f"Processing response with {len(response.candidates[0].content.parts)} parts")
            images_sent = 0
            for index, part in enumerate(response.candidates[0].content.parts):
                logging.info(f"Part {index}: type={type(part)}, has_inline_data={hasattr(part, 'inline_data')}")
                logging.info(f"Part {index} attributes: {dir(part)}")
                if hasattr(part, "inline_data") and part.inline_data and hasattr(part.inline_data, 'data') and part.inline_data.data:
                    logging.info(f"Part {index} inline_data: {part.inline_data}")
                    logging.info(f"Part {index} mime_type: {part.inline_data.mime_type}")
                    logging.info(f"Part {index} data length: {len(part.inline_data.data)}")
                    
                    # Create filename with timestamp
                    timestamp = datetime.now().strftime("%H_%M_%S_%m%d%Y_%s")
                    filename = f"generated_image_{timestamp}_part{index}.png"

                    # Send the image
                    try:
                        file = discord.File(
                            fp=io.BytesIO(part.inline_data.data), filename=filename
                        )
                        logging.info(f"Created Discord file: {filename}")

                        await ctx.send(
                            f"🎨 **Generated Image {index + 1}**\nPrompt: *{prompt}*",
                            file=file,
                        )
                        logging.info(f"Successfully sent image {index + 1}")
                        images_sent += 1
                    except Exception as e:
                        logging.error(f"Error sending image {index + 1}: {e}")
                        # Try to send without file as fallback
                        await ctx.send(f"❌ Error sending image {index + 1}: {str(e)[:100]}")
                elif hasattr(part, 'text') and part.text:
                    logging.info(f"Part {index} contains text response: {part.text[:200]}...")
                    # Truncate long text responses to fit Discord's 2000 character limit
                    text_content = part.text
                    if len(text_content) > 1900:  # Leave room for formatting
                        text_content = text_content[:1900] + "... [truncated]"
                    
                    # Check if it's an error message
                    if "violates the policy" in part.text.lower() or "unable to create" in part.text.lower():
                        await ctx.send(f"❌ **Content Policy Violation**\n{text_content}")
                    else:
                        await ctx.send(f"ℹ️ **API Response**\n{text_content}")
                else:
                    logging.warning(f"Part {index} has no inline_data or inline_data is False/None")
                    logging.info(f"Part {index} content: {part}")

            if images_sent > 0:
                await status_msg.edit(
                    content=f"✅ Successfully generated {images_sent} image(s)!"
                )
            else:
                await status_msg.edit(
                    content="❌ No images were generated. Please try again."
                )

        except Exception as e:
            logging.error(f"Error generating image: {e}")
            error_msg = str(e)
            
            # Handle Discord API errors specifically
            if "400 Bad Request" in error_msg and "2000 or fewer" in error_msg:
                await status_msg.edit(content="❌ **Discord Error**: Response too long. Please try a shorter prompt.")
            elif "400 Bad Request" in error_msg:
                await status_msg.edit(content="❌ **Discord Error**: Bad request. Please try again.")
            else:
                # Truncate error message if it's too long
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                await status_msg.edit(content=f"❌ Error generating image: {error_msg}")

    @commands.slash_command(
        name="edit_image", description="Edit an existing image using AI"
    )
    async def edit_image(self, ctx, prompt: str, temperature: float = 0.7):
        """Edit an image using Gemini AI. Attach an image to your message first."""
        if not self._gemini_api_configured:
            await ctx.respond(
                "❌ Image editing is not available. Please check the bot configuration.",
                ephemeral=True,
            )
            return

        # Check if there's an image attachment
        if not ctx.message.attachments:
            await ctx.respond(
                "❌ Please attach an image to edit. Reply to this message with an image attachment.",
                ephemeral=True,
            )
            return

        image_attachment = ctx.message.attachments[0]

        # Validate image
        if (
            not image_attachment.content_type
            or not image_attachment.content_type.startswith("image/")
        ):
            await ctx.respond("❌ Please attach a valid image file.", ephemeral=True)
            return

        if image_attachment.size > 10 * 1024 * 1024:  # 10MB limit
            await ctx.respond(
                "❌ Image file is too large. Please use an image smaller than 10MB.",
                ephemeral=True,
            )
            return

        # Check temperature limits
        if temperature < 0.0 or temperature > 1.2:
            await ctx.respond(
                "❌ Temperature must be between 0.0 and 1.2", ephemeral=True
            )
            return

        # Send initial status message
        status_msg = await ctx.respond(
            f"⌛ Editing image with prompt: **{prompt}**... This may take a few minutes."
        )

        try:
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_attachment.url) as response:
                    if response.status != 200:
                        await status_msg.edit(
                            content="❌ Failed to download the image. Please try again."
                        )
                        return

                    image_data = await response.read()

            # Get the model for image generation - use a model that supports image generation
            model_name = environ.get("DEFAULT_GEMINI_IMAGE_GENERATION_MODEL", "gemini-2.0-flash-preview-image-generation")
            if not model_name or model_name == "gemini-model-id":
                model_name = "gemini-2.0-flash-preview-image-generation"  # Fallback to a model that supports image generation
            
            logging.info(f"Using image editing model: {model_name}")
            model = genai.GenerativeModel(model_name=model_name)

            # Create the prompt with image
            image_part = types.Part.from_bytes(
                data=image_data, mime_type=image_attachment.content_type
            )

            # Generate the edited image with safety settings disabled
            response = await model.generate_content_async(
                contents=[prompt, image_part],
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 8192,
                    "response_modalities": ["IMAGE"]
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )

            if not response.candidates or not response.candidates[0].content:
                await status_msg.edit(
                    content="❌ Failed to edit image. Please try again."
                )
                return

            # Check for safety issues
            if response.candidates[0].finish_reason == "IMAGE_SAFETY":
                await status_msg.edit(
                    content="❌ Image editing blocked by safety filters. Please try a different prompt."
                )
                return

            # Process and send edited images
            images_sent = 0
            for index, part in enumerate(response.candidates[0].content.parts):
                if hasattr(part, "inline_data") and part.inline_data:
                    # Create filename with timestamp
                    timestamp = datetime.now().strftime("%H_%M_%S_%m%d%Y_%s")
                    filename = f"edited_image_{timestamp}_part{index}.png"

                    # Send the edited image
                    file = discord.File(
                        fp=io.BytesIO(part.inline_data.data), filename=filename
                    )

                    await ctx.send(
                        f"🎨 **Edited Image {index + 1}**\nPrompt: *{prompt}*",
                        file=file,
                    )
                    images_sent += 1

            if images_sent > 0:
                await status_msg.edit(
                    content=f"✅ Successfully edited {images_sent} image(s)!"
                )
            else:
                await status_msg.edit(
                    content="❌ No edited images were generated. Please try again."
                )

        except Exception as e:
            logging.error(f"Error editing image: {e}")
            await status_msg.edit(content=f"❌ Error editing image: {str(e)[:100]}")

    @commands.slash_command(
        name="image_help", description="Show help for image generation commands"
    )
    async def image_help(self, ctx):
        """Show help information for image generation commands."""
        embed = discord.Embed(
            title="🎨 Image Generation Commands",
            description="Generate and edit images using AI without needing the AI to use tools!",
            color=0x00FF00,
        )

        embed.add_field(
            name="/generate_image",
            value="Generate a new image from a text prompt\n**Usage:** `/generate_image <prompt> [temperature]`\n**Example:** `/generate_image a cute robot playing guitar`",
            inline=False,
        )

        embed.add_field(
            name="/edit_image",
            value="Edit an existing image. Attach an image first!\n**Usage:** `/edit_image <prompt> [temperature]`\n**Example:** `/edit_image add a hat` (with image attached)",
            inline=False,
        )

        embed.add_field(
            name="/auto_image",
            value="Toggle automatic image generation mode (Admin only)\n**Usage:** `/auto_image [true/false]`\n**Effect:** Jakey automatically generates images for simple requests",
            inline=False,
        )

        embed.add_field(
            name="/auto_image_status",
            value="Check current auto-image generation status for this server\n**Usage:** `/auto_image_status`\n**Shows:** Current mode, what it means, and admin controls",
            inline=False,
        )

        embed.add_field(
            name="🤖 Auto-Generation Mode",
            value="When enabled, Jakey will automatically detect image requests and generate images instantly!\n**Example:** Say 'draw me a cat' and Jakey will generate it automatically.\n**Persistence:** Settings are saved to database and survive bot restarts.",
            inline=False,
        )

        embed.add_field(
            name="Temperature",
            value="Controls creativity (0.0 = focused, 1.2 = very creative)\n**Default:** 0.7",
            inline=False,
        )

        embed.add_field(
            name="Tips",
            value="• Be specific in your prompts\n• For editing, keep prompts simple\n• Images are generated in PNG format\n• Maximum file size: 10MB\n• Auto-generation works best with detailed prompts",
            inline=False,
        )

        embed.set_footer(text="Powered by Gemini AI")
        await ctx.respond(embed=embed, ephemeral=True)

    async def _load_auto_image_settings(self):
        """Load auto-image generation settings from the database."""
        await self.bot.wait_until_ready()

        try:
            if not self.DBConn:
                logging.warning(
                    "No database connection available for loading auto-image settings"
                )
                return

            # Get all guilds and load their auto-image settings
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                try:
                    # Try to get the setting from the database
                    setting = await self._get_auto_image_setting(guild_id)
                    self._auto_image_enabled[guild_id] = setting
                    logging.info(
                        f"Loaded auto-image setting for guild {guild.name}: {setting}"
                    )
                except Exception as e:
                    logging.warning(
                        f"Failed to load auto-image setting for guild {guild.name}: {e}"
                    )
                    # Default to disabled if loading fails
                    self._auto_image_enabled[guild_id] = False

            logging.info(
                f"Loaded auto-image settings for {len(self._auto_image_enabled)} guilds"
            )

        except Exception as e:
            logging.error(f"Error loading auto-image settings: {e}")

    async def _get_auto_image_setting(self, guild_id: str) -> bool:
        """Get auto-image setting from database for a specific guild."""
        try:
            if not self.DBConn:
                return False

            # Use the existing database structure to store auto-image settings
            # We'll store it in the guild's main document
            guild_doc = await self.DBConn._collection.find_one({"guild_id": guild_id})

            if guild_doc and "auto_image_enabled" in guild_doc:
                return guild_doc["auto_image_enabled"]
            else:
                # Default to disabled if no setting found
                return False

        except Exception as e:
            logging.error(f"Error getting auto-image setting for guild {guild_id}: {e}")
            return False

    async def _save_auto_image_setting(self, guild_id: str, enabled: bool) -> bool:
        """Save auto-image setting to database for a specific guild."""
        try:
            if not self.DBConn:
                logging.warning(
                    "No database connection available for saving auto-image setting"
                )
                return False

            # Update the guild's document with the auto-image setting
            result = await self.DBConn._collection.update_one(
                {"guild_id": guild_id},
                {
                    "$set": {
                        "auto_image_enabled": enabled,
                        "auto_image_updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )

            if result.modified_count > 0 or result.upserted_id:
                logging.info(
                    f"Saved auto-image setting for guild {guild_id}: {enabled}"
                )
                return True
            else:
                logging.warning(
                    f"No changes made when saving auto-image setting for guild {guild_id}"
                )
                return False

        except Exception as e:
            logging.error(f"Error saving auto-image setting for guild {guild_id}: {e}")
            return False

    @commands.slash_command(
        name="auto_image_status",
        description="Check the current auto-image generation status for this server",
    )
    async def auto_image_status(self, ctx):
        """Check the current auto-image generation status."""
        guild_id = str(ctx.guild.id)
        current_setting = self._auto_image_enabled.get(guild_id, False)

        embed = discord.Embed(
            title="🎨 Auto-Image Generation Status",
            color=0x00FF00 if current_setting else 0xFF0000,
        )

        if current_setting:
            embed.description = "✅ **Auto-Image Generation is ENABLED**"
            embed.add_field(
                name="Current Mode",
                value="🤖 **Automatic Generation**\nJakey will automatically generate images for simple requests.",
                inline=False,
            )
            embed.add_field(
                name="What This Means",
                value="• Users can say 'draw me a cat' and get images automatically\n• No need to remember command syntax\n• Faster image generation for simple requests",
                inline=False,
            )
        else:
            embed.description = "❌ **Auto-Image Generation is DISABLED**"
            embed.add_field(
                name="Current Mode",
                value="💡 **Suggestion Mode**\nJakey will suggest image generation commands but won't generate automatically.",
                inline=False,
            )
            embed.add_field(
                name="What This Means",
                value="• Users must use `/generate_image` or `/edit_image` commands\n• Full control over image generation process\n• Manual command usage required",
                inline=False,
            )

        embed.add_field(
            name="Admin Control",
            value="Use `/auto_image [true/false]` to change this setting\nRequires 'Manage Channels' permission",
            inline=False,
        )

        embed.add_field(
            name="Persistence",
            value="✅ Settings are saved to database and survive bot restarts",
            inline=False,
        )

        embed.set_footer(text=f"Server: {ctx.guild.name}")
        await ctx.respond(embed=embed, ephemeral=True)

    async def _handle_new_guild(self, guild):
        """Handle a new guild joining and initialize auto-image settings."""
        try:
            guild_id = str(guild.id)

            # Check if we already have a setting for this guild
            if guild_id not in self._auto_image_enabled:
                # Load the setting from database (or default to False)
                setting = await self._get_auto_image_setting(guild_id)
                self._auto_image_enabled[guild_id] = setting
                logging.info(
                    f"Initialized auto-image setting for new guild {guild.name}: {setting}"
                )

        except Exception as e:
            logging.error(f"Error handling new guild {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Handle when the bot joins a new guild."""
        await self._handle_new_guild(guild)


def setup(bot):
    bot.add_cog(Misc(bot))
