import logging
import discord
from discord.ext import commands
from discord import Member
from datetime import datetime, timedelta, timezone
from os import environ
import aiohttp
import io
import time
import asyncio
import re


class Misc(commands.Cog):
    """Use my other utilities here that can help make your server more active and entertaining"""

    def __init__(self, bot):
        self.bot = bot
        self.DBConn = getattr(bot, "DBConn", None)

        # Initialize auto-image settings dictionary
        self._auto_image_enabled = {}
        self._auto_image_loaded = False  # Track if settings have been loaded

        # Start reminder checker if database is available
        if self.DBConn:
            self.bot.loop.create_task(self._check_reminders())
            logging.info("Reminder checker started")
        else:
            logging.warning("Reminder checker not started - no database connection")

        # Pollinations.AI is the primary AI provider
        pass

        # Initialize auto-image settings and load from database
        if self.DBConn:
            self.bot.loop.create_task(self._load_auto_image_settings())
            logging.info("Auto-image settings loader started")
        else:
            logging.warning(
                "Auto-image settings loader not started - no database connection"
            )
            # Try to initialize later when DBConn becomes available
            self.bot.loop.create_task(self._wait_for_db_and_init())

    async def _wait_for_db_and_init(self):
        """Wait for database connection to become available and initialize services."""
        await self.bot.wait_until_ready()

        # Wait up to 30 seconds for DBConn to be initialized
        for _ in range(30):
            if hasattr(self.bot, "DBConn") and self.bot.DBConn is not None:
                self.DBConn = self.bot.DBConn
                logging.info(
                    "Database connection became available, initializing services..."
                )

                # Start reminder checker
                self.bot.loop.create_task(self._check_reminders())
                logging.info("Reminder checker started")

                # Load auto-image settings
                self.bot.loop.create_task(self._load_auto_image_settings())
                logging.info("Auto-image settings loader started")
                return

            await asyncio.sleep(1)

        logging.warning("Database connection not available after 30 seconds")

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
        guild_ids=None,  # Global command
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

            await self.DBConn.add_reminder(
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
        guild_ids=None,  # Global command
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
        """Automatically generate an image for a user request using Pollinations.AI ImageGen tool when available."""

        # Check for image attachments or URLs in the message for editing
        image_urls = []
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith(
                    "image/"
                ):
                    image_urls.append(attachment.url)

        # Also check for URLs in the message content
        import re

        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        found_urls = re.findall(url_pattern, message.content)
        for url in found_urls:
            if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                image_urls.append(url)

        # Check if Pollinations.AI is available and try to use ImageGen tool
        try:
            # Try to use the new ImageGen tool with Pollinations.AI
            from tools.ImageGen.tool import Tool as ImageGenTool

            # Create a mock context for the tool
            async def send_method(content=None, file=None, embed=None):
                if file:
                    sent_msg = await message.channel.send(
                        f"🎨 **Auto-Generated Image**\nPrompt: *{prompt}*",
                        file=file,
                        reference=message,
                    )
                    return sent_msg
                elif embed:
                    # Handle embed messages
                    sent_msg = await message.channel.send(
                        embed=embed,
                        reference=message,
                    )
                    return sent_msg
                elif content:
                    # Remove or modify links to prevent previews
                    import re

                    # Replace http/https links with a format that won't generate previews
                    modified_content = re.sub(
                        r"https?://[^\s]+",
                        lambda m: f"[{m.group(0)}]({m.group(0)})",
                        content,
                    )
                    sent_msg = await message.channel.send(
                        modified_content,
                        reference=message,
                    )
                    return sent_msg

            # Initialize the ImageGen tool
            image_gen_tool = ImageGenTool(
                method_send=send_method, discord_ctx=message, discord_bot=self.bot
            )

            # Generate image using Pollinations.AI with URL context if available
            if image_urls:
                status_msg = await message.channel.send(
                    f"🎨 **Auto-Editing Image (Pollinations.AI)**\n"
                    f"Prompt: *{prompt}*\n"
                    f"Images: {len(image_urls)} image(s) to edit\n"
                    f"⌛ This may take a few minutes...",
                    reference=message,
                )
                await image_gen_tool._tool_function(
                    prompt=prompt, url_context=image_urls
                )
            else:
                status_msg = await message.channel.send(
                    f"🎨 **Auto-Generating Image (Pollinations.AI)**\n"
                    f"Prompt: *{prompt}*\n"
                    f"⌛ This may take a few minutes...",
                    reference=message,
                )
                await image_gen_tool._tool_function(prompt=prompt)

            await status_msg.edit(content="✅ Auto-generation completed successfully!")

            return True

        except Exception as pollinations_error:
            logging.warning(f"Pollinations.AI ImageGen failed: {pollinations_error}")
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and automatically offer image generation when appropriate."""
        # Ignore bot messages and commands
        if message.author.bot or message.content.startswith("/"):
            return

        # Wait for auto-image settings to be loaded if not already
        if not self._auto_image_loaded:
            logging.debug(
                "Auto-image settings not loaded yet, skipping message processing"
            )
            return

        # Check if the message is directed at the bot (mention or prefix command)
        bot_mentioned = self.bot.user in message.mentions

        # Get the bot's command prefix and check for common variations
        prefix = getattr(self.bot, "command_prefix", "!")
        possible_prefixes = [prefix, "jakey", "Jakey"]
        starts_with_prefix = any(
            message.content.startswith(p) for p in possible_prefixes
        )

        # Only proceed if the message is directed at the bot
        if not (bot_mentioned or starts_with_prefix):
            return

        # Check if the message is asking for image generation or editing
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
            "edit this image",
            "modify this image",
            "change this image",
            "update this image",
            "improve this image",
            "enhance this image",
        ]

        message_lower = message.content.lower()
        is_image_request = any(keyword in message_lower for keyword in image_keywords)

        if is_image_request:
            # Extract potential prompt from the message
            prompt = self._extract_image_prompt(message.content)

            # Check if auto-generation is enabled for this guild
            guild_id = str(message.guild.id) if message.guild else "dm"
            auto_enabled = self._auto_image_enabled.get(guild_id, False)

            logging.debug(
                f"Auto-image request detected. Guild: {guild_id}, Enabled: {auto_enabled}, Prompt: {prompt}"
            )

            if (
                auto_enabled and len(prompt) > 3
            ):  # Only auto-generate for substantial prompts
                # Try to auto-generate the image
                success = await self._auto_generate_image(message, prompt)
                if success:
                    return  # Don't send the suggestion if auto-generation succeeded

            # Create a helpful response with image generation options
            embed = discord.Embed(
                title="🎨 Image Generation Detected!",
                description="I detected you're asking for an image! Here are your options:",
                color=0x00FF00,
            )

            embed.add_field(
                name="🖼️ Generate New Image (Pollinations.AI)",
                value=f"Use `/generate_image {prompt}` to create a new image with Pollinations.AI",
                inline=False,
            )

            embed.add_field(
                name="🎨 Generate with Pollinations.AI (Advanced)",
                value="Use the new ImageGen tool for advanced image generation with Pollinations.AI (auto-enabled)",
                inline=False,
            )

            embed.add_field(
                name="🎭 Generate with Pollinations.AI",
                value=f"Use `/generate_image {prompt}` for creative images",
                inline=False,
            )

            embed.add_field(
                name="✏️ Edit Existing Image",
                value="Attach an image and use the ImageGen tool with URL context to modify it with Pollinations.AI",
                inline=False,
            )

            embed.add_field(
                name="❓ Need Help?",
                value="Use `/image_help` for detailed instructions",
                inline=False,
            )

            embed.set_footer(
                text="💡 Tip: Use different models (flux, kontext, sdxl) for different styles"
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        name="mimic",
        description="Mimic as another user",
        guild_ids=None,  # Global command
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
            name=f"Mimic command by {ctx.author}"
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        guild_ids=None,  # Global command
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
        name="auto_tool_sensitivity",
        description="Adjust auto-tool detection sensitivity settings.",
        guild_ids=None,  # Global command
    )
    @discord.option(
        "action",
        description="What action to perform",
        choices=["view", "set_global", "set_tool", "reset_user", "reset_all"],
        required=True,
    )
    @discord.option(
        "setting",
        description="Setting to adjust (for set_global and set_tool actions)",
        required=False,
    )
    @discord.option(
        "value",
        description="New value for the setting (for set_global and set_tool actions)",
        required=False,
    )
    @discord.option(
        "tool_name",
        description="Tool name (for set_tool action)",
        choices=[
            "ExaSearch",
            "CryptoPrice",
            "CurrencyConverter",
            "CodeExecution",
            "Memory",
        ],
        required=False,
    )
    async def auto_tool_sensitivity(
        self,
        ctx,
        action: str,
        setting: str = None,
        value: str = None,
        tool_name: str = None,
    ):
        """Adjust auto-tool detection sensitivity settings."""
        await ctx.response.defer(ephemeral=True)

        # Check if user has admin permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "❌ You need administrator permissions to adjust auto-tool sensitivity settings."
            )
            return

        try:
            # Import the auto-tool detector
            from core.services.auto_tool_detector import AutoToolDetector

            # Get or create detector instance
            if not hasattr(self.bot, "auto_tool_detector"):
                self.bot.auto_tool_detector = AutoToolDetector()

            detector = self.bot.auto_tool_detector

            if action == "view":
                # View current settings
                config = detector.get_config()

                # Format global settings
                global_settings = config.get("global", {})
                global_text = f"**Global Settings:**\n"
                global_text += (
                    f"• **Enabled**: {global_settings.get('enabled', True)}\n"
                )
                global_text += f"• **Confidence Threshold**: {global_settings.get('confidence_threshold', 0.8):.2f}\n"
                global_text += f"• **Min Message Length**: {global_settings.get('min_message_length', 3)}\n"
                global_text += f"• **Require Explicit Keywords**: {global_settings.get('require_explicit_keywords', True)}\n"

                # Format tool settings
                tools_text = "**Tool-Specific Settings:**\n"
                for tool, settings in config.get("tools", {}).items():
                    threshold = settings.get("confidence_threshold", 0.8)
                    enabled = settings.get("enabled", True)
                    tools_text += f"• **{tool}**: {threshold:.2f} threshold, {'enabled' if enabled else 'disabled'}\n"

                # Format advanced settings
                advanced_settings = config.get("advanced", {})
                advanced_text = f"**Advanced Settings:**\n"
                advanced_text += f"• **Cooldown Period**: {advanced_settings.get('cooldown_period', 60)}s\n"
                advanced_text += f"• **Repetition Penalty**: {advanced_settings.get('repetition_penalty', 0.15):.2f}\n"
                advanced_text += f"• **Learn User Preferences**: {advanced_settings.get('learn_user_preferences', True)}\n"

                await ctx.respond(
                    f"🔧 **Auto-Tool Detection Settings**\n\n{global_text}\n{tools_text}\n{advanced_text}"
                )

            elif action == "set_global":
                if not setting or not value:
                    await ctx.respond(
                        "❌ Please provide both setting and value for set_global action."
                    )
                    return

                # Parse value based on setting type
                if setting in [
                    "enabled",
                    "require_explicit_keywords",
                    "fuzzy_matching",
                ]:
                    parsed_value = value.lower() in ["true", "1", "yes", "on"]
                elif setting in ["confidence_threshold"]:
                    try:
                        parsed_value = float(value)
                        if not 0.0 <= parsed_value <= 1.0:
                            await ctx.respond(
                                "❌ Confidence threshold must be between 0.0 and 1.0"
                            )
                            return
                    except ValueError:
                        await ctx.respond("❌ Invalid confidence threshold value")
                        return
                elif setting in ["min_message_length", "max_message_length"]:
                    try:
                        parsed_value = int(value)
                        if parsed_value < 0:
                            await ctx.respond("❌ Message length must be 0 or positive")
                            return
                    except ValueError:
                        await ctx.respond("❌ Invalid message length value")
                        return
                else:
                    await ctx.respond(f"❌ Unknown global setting: {setting}")
                    return

                # Update configuration
                config = detector.get_config()
                if "global" not in config:
                    config["global"] = {}
                config["global"][setting] = parsed_value
                detector.update_config(config)

                await ctx.respond(
                    f"✅ Updated global setting **{setting}** to **{parsed_value}**"
                )

            elif action == "set_tool":
                if not tool_name or not setting or not value:
                    await ctx.respond(
                        "❌ Please provide tool_name, setting, and value for set_tool action."
                    )
                    return

                # Parse value based on setting type
                if setting in [
                    "enabled",
                    "require_both_keywords",
                    "require_conversion_format",
                    "require_explicit_calc",
                    "require_explicit_memory",
                    "require_sports_context",
                ]:
                    parsed_value = value.lower() in ["true", "1", "yes", "on"]
                elif setting in ["confidence_threshold"]:
                    try:
                        parsed_value = float(value)
                        if not 0.0 <= parsed_value <= 1.0:
                            await ctx.respond(
                                "❌ Confidence threshold must be between 0.0 and 1.0"
                            )
                            return
                    except ValueError:
                        await ctx.respond("❌ Invalid confidence threshold value")
                        return
                elif setting in ["min_weak_keywords"]:
                    try:
                        parsed_value = int(value)
                        if parsed_value < 1:
                            await ctx.respond(
                                "❌ Min weak keywords must be 1 or greater"
                            )
                            return
                    except ValueError:
                        await ctx.respond("❌ Invalid min weak keywords value")
                        return
                else:
                    await ctx.respond(f"❌ Unknown tool setting: {setting}")
                    return

                # Update configuration
                config = detector.get_config()
                if "tools" not in config:
                    config["tools"] = {}
                if tool_name not in config["tools"]:
                    config["tools"][tool_name] = {}
                config["tools"][tool_name][setting] = parsed_value
                detector.update_config(config)

                await ctx.respond(
                    f"✅ Updated **{tool_name}** setting **{setting}** to **{parsed_value}**"
                )

            elif action == "reset_user":
                # Reset user preferences
                user_id = ctx.author.id
                detector.reset_user_preferences(user_id)
                await ctx.respond(
                    f"✅ Reset auto-tool preferences for user <@{user_id}>"
                )

            elif action == "reset_all":
                # Reset all user preferences
                detector.user_preferences.clear()
                detector.last_activations.clear()
                detector.activation_counts.clear()
                await ctx.respond("✅ Reset all user auto-tool preferences")

            else:
                await ctx.respond(f"❌ Unknown action: {action}")

        except Exception as e:
            logging.error(f"Error in auto_tool_sensitivity command: {e}")
            await ctx.respond(f"❌ Error adjusting sensitivity settings: {str(e)}")

    @commands.slash_command(
        name="generate_image",
        description="Generate an image using Pollinations.AI",
        guild_ids=None,  # Global command
    )
    async def generate_image(
        self,
        ctx,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
    ):
        """Generate an image using Pollinations.AI - great for creative and artistic prompts."""
        # Send initial status message
        status_msg = await ctx.respond(
            f"🎨 Generating image with Pollinations.AI...\nPrompt: **{prompt}**\nModel: **{model}**\nSize: **{width}x{height}**"
        )

        try:
            # Import the Pollinations model
            from aimodels.pollinations.infer import Completions

            # Create the model instance
            pollinations_model = Completions(
                model_name=f"pollinations::{model}",
                discord_ctx=ctx,
                discord_bot=self.bot,
                guild_id=ctx.guild.id if ctx.guild else None,
            )

            # Set image parameters
            pollinations_model._genai_params["width"] = width
            pollinations_model._genai_params["height"] = height

            # Generate the image
            image_url = await pollinations_model._generate_image(prompt)

            # Send the image URL
            await ctx.send(
                f"🎨 **Generated Image**\nPrompt: *{prompt}*\nModel: *{model}*\nSize: *{width}x{height}*\n\n{image_url}"
            )

            await status_msg.edit(content="✅ Image generated successfully!")

        except Exception as e:
            logging.error(f"Error generating image with Pollinations: {e}")
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            await status_msg.edit(content=f"❌ Error generating image: {error_msg}")

    @commands.slash_command(
        name="image_help",
        description="Show help for image generation commands",
        guild_ids=None,  # Global command
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
            value="Generate an image using Pollinations.AI\n**Usage:** `/generate_image <prompt> [model] [width] [height]`\n**Example:** `/generate_image a beautiful sunset`",
            inline=False,
        )

        embed.add_field(
            name="🎨 Image-to-Image Generation",
            value="Use the ImageGen tool with URL context for image editing\n**Usage:** Provide image URL in the tool context\n**Example:** Use the ImageGen tool with an image URL to edit/remix it",
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
            name="/reload_auto_image_settings",
            value="Force reload auto-image settings from database (Admin only)\n**Usage:** `/reload_auto_image_settings`\n**Effect:** Refreshes settings without restarting the bot",
            inline=False,
        )

        embed.add_field(
            name="🤖 Auto-Generation Mode",
            value="When enabled, Jakey will automatically detect image requests and generate images instantly!\n**Important:** Only works when you mention Jakey or use prefix commands.\n**Example:** '@Jakey draw me a cat' or '!draw me a cat' will trigger auto-generation.\n**Persistence:** Settings are saved to database and survive bot restarts.",
            inline=False,
        )

        embed.add_field(
            name="Models",
            value="**Flux**: High-quality text-to-image\n**Kontext**: Image-to-image editing\n**SDXL**: Alternative generation style\n**Default:** flux",
            inline=False,
        )

        embed.add_field(
            name="Tips",
            value="• Be specific in your prompts\n• For editing, keep prompts simple\n• Images are generated in PNG format\n• Maximum file size: 10MB\n• Auto-generation works best with detailed prompts",
            inline=False,
        )

        embed.set_footer(text="Powered by Pollinations.AI")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="reload_auto_image_settings",
        description="Force reload auto-image settings from database (Admin only)",
        guild_ids=None,  # Global command
    )
    @commands.has_permissions(manage_channels=True)
    async def reload_auto_image_settings(self, ctx):
        """Force reload auto-image settings from database."""
        await ctx.response.defer(ephemeral=True)

        try:
            # Clear current settings and reload from database
            self._auto_image_enabled.clear()
            self._auto_image_loaded = False

            # Reload settings
            await self._load_auto_image_settings()

            guild_id = str(ctx.guild.id)
            current_setting = self._auto_image_enabled.get(guild_id, False)

            await ctx.followup.send(
                f"🔄 **Auto-Image Settings Reloaded!**\n"
                f"Current status for this server: {'✅ Enabled' if current_setting else '❌ Disabled'}\n"
                f"Total guilds loaded: {len(self._auto_image_enabled)}\n"
                f"✅ Settings refreshed from database successfully!",
                ephemeral=True,
            )

        except Exception as e:
            logging.error(f"Error reloading auto-image settings: {e}")
            await ctx.followup.send(
                f"❌ **Failed to reload settings!**\n"
                f"Error: {str(e)}\n"
                f"Please try again or contact an administrator.",
                ephemeral=True,
            )

    async def _load_auto_image_settings(self):
        """Load auto-image generation settings from the database."""
        await self.bot.wait_until_ready()

        try:
            if not self.DBConn:
                logging.warning(
                    "No database connection available for loading auto-image settings"
                )
                self._auto_image_loaded = True  # Mark as loaded even if no DB
                return

            # Get all guilds and load their auto-image settings
            loaded_count = 0
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                try:
                    # Try to get the setting from the database
                    setting = await self._get_auto_image_setting(guild_id)
                    self._auto_image_enabled[guild_id] = setting
                    loaded_count += 1
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
                f"Successfully loaded auto-image settings for {loaded_count}/{len(self.bot.guilds)} guilds"
            )

        except Exception as e:
            logging.error(f"Error loading auto-image settings: {e}")
        finally:
            # Mark as loaded regardless of success/failure
            self._auto_image_loaded = True
            logging.info("Auto-image settings loading completed")

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
        name="auto_image_debug",
        description="Debug auto-image generation system (Admin only)",
        guild_ids=None,  # Global command
    )
    @commands.has_permissions(manage_channels=True)
    async def auto_image_debug(self, ctx):
        """Debug auto-image generation system."""
        guild_id = str(ctx.guild.id)

        embed = discord.Embed(
            title="🔧 Auto-Image Generation Debug",
            color=0x0099FF,
        )

        # System status
        embed.add_field(
            name="System Status",
            value=f"• Settings Loaded: {'✅' if self._auto_image_loaded else '❌'}\n• Pollinations.AI: ✅\n• Database: {'✅' if self.DBConn else '❌'}",
            inline=False,
        )

        # Current settings
        current_setting = self._auto_image_enabled.get(guild_id, False)
        embed.add_field(
            name="Current Settings",
            value=f"• Guild ID: `{guild_id}`\n• Auto-Image Enabled: {'✅' if current_setting else '❌'}\n• Total Guilds Loaded: {len(self._auto_image_enabled)}",
            inline=False,
        )

        # Test auto-generation
        embed.add_field(
            name="Test Auto-Generation",
            value="✅ Ready to test\nUse: `@Jakey draw me a test image`",
            inline=False,
        )

        embed.set_footer(text=f"Server: {ctx.guild.name}")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="auto_image_status",
        description="Check the current auto-image generation status for this server",
        guild_ids=None,  # Global command
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
            name="System Status",
            value=f"• Settings Loaded: {'✅' if self._auto_image_loaded else '❌'}\n• Pollinations.AI: ✅\n• Database: {'✅' if self.DBConn else '❌'}",
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

    @commands.slash_command(
        name="help",
        description="Get help and quickstart guide for Jakey Bot",
        guild_ids=None,  # Global command
    )
    async def help_command(self, ctx):
        """Show comprehensive help and quickstart guide"""
        # Create multiple embeds to stay within Discord's character limits

        # Main Help Embed
        main_embed = discord.Embed(
            title="🤖 Jakey The Degenerate Bot - Help Guide",
            description="Your AI-powered Discord companion with multi-model support, tools, and degenerate gambling expertise!",
            color=discord.Color.blue(),
        )

        # Auto Tool Switch System
        main_embed.add_field(
            name="🔄 **Auto Tool Switch System** ⭐ **NEW FEATURE**",
            value="**Just ask naturally** - JakeyBot automatically detects what tool you need!\n\n"
            "**Examples:**\n"
            "• `What's the price of Bitcoin?` → 🔄 **Auto-enabled CryptoPrice**\n"
            "• `Search for latest AI news` → 🔄 **Auto-enabled ExaSearch**\n"
            "• `Convert 100 USD to EUR` → 🔄 **Auto-enabled CurrencyConverter**\n\n"
            "**Key Benefits:**\n"
            "✅ **No Manual Tool Switching** - Tools enable automatically when needed\n"
            "✅ **Smart Timeout Management** - Tools return to Memory after optimal timeouts\n"
            "✅ **Intelligent Suggestions** - Get optimization tips with `/smart_suggestions`\n"
            "✅ **Seamless Experience** - Focus on your questions, not tool management",
            inline=False,
        )

        # Quickstart section
        main_embed.add_field(
            name="🚀 **Quick Start**",
            value="1️⃣ **Ask Questions**: Mention Jakey with your question\n2️⃣ **Let Tools Auto-Enable**: Most tools activate automatically when needed\n3️⃣ **Explore More**: Use `/help commands` for all commands and `/help models` for AI models",
            inline=False,
        )

        # Core commands
        main_embed.add_field(
            name="📋 **Essential Commands**",
            value="• Mention Jakey with your question\n• `/model set <model>` - Switch AI models (Admin only)\n• `/model current` - Show current model\n• `/model list` - List all available models\n• `/feature <tool>` - Enable tools\n• `/sweep` - Clear conversation and reset\n• `/quickstart` - Get step-by-step guide\n• Use `/help commands` for complete command list",
            inline=False,
        )

        main_embed.set_footer(
            text="Jakey Bot v2.1.0 - DEGEN Edition | Page 1 of 3"
        )

        # Commands Help Embed
        commands_embed = discord.Embed(
            title="🤖 Jakey Bot - Commands Guide",
            description="Complete list of available commands",
            color=discord.Color.green(),
        )

        # Auto-Return System Commands
        commands_embed.add_field(
            name="🔄 **Auto-Return System**",
            value="• `/smart_suggestions` - Get optimization tips\n• `/extend_timeout <time>` - Extend tool session time\n• `/timeout_status` - Check remaining time\n• `/return_to_default` - Return to Memory immediately\n• `/auto_return_status` - View system status\n• `/auto_tool_sensitivity` - Adjust auto-tool detection sensitivity",
            inline=False,
        )

        # Tools
        commands_embed.add_field(
            name="🛠️ **Available Tools**",
            value="• **Memory** - Remember and recall information\n• **ExaSearch** - Enhanced web search with smart caching\n• **CryptoPrice** - Live token prices\n• **CurrencyConverter** - 170+ currency conversion\n\n• **ImageGen** - AI image generation\n• **CodeExecution** - Python code execution\n• **Engagement** - Channel participation\n• **GamblingGames** - Betting pools and trivia",
            inline=False,
        )

        # Advanced features
        commands_embed.add_field(
            name="⚡ **Advanced Features**",
            value="• **Enhanced Web Search**: Smart query enhancement, quality scoring, caching\n• **Search Statistics**: `/search_stats` for performance metrics\n• **Image Generation**: `/generate_image <prompt>`\n• **Image Editing**: Use ImageGen tool with URL context\n• **Auto-Image**: Automatic detection\n• **Reminders**: `/remind <time> <message>`\n• **Trivia Games**: `/trivia` for challenges\n• **Gambling Games**: `/create_bet` for pools\n• **Keno Numbers**: `/keno` for random numbers\n• **Engagement**: `/jakey_engage` for participation\n• **Music**: `/play <query>` for music",
            inline=False,
        )

        # Music commands
        commands_embed.add_field(
            name="🎵 **Music Commands**",
            value="• `/play <query>` - Play from YouTube/Spotify\n"
            "• `/pause` - Pause playback\n"
            "• `/resume` - Resume playback\n"
            "• `/stop` - Stop and clear queue\n"
            "• `/skip` - Vote to skip track\n"
            "• `/queue` - Show current queue\n"
            "• `/nowplaying` - Show current track\n"
            "• `/volume <0-100>` - Set volume level\n"
            "• `/disconnect` - Leave voice channel",
            inline=False,
        )

        commands_embed.set_footer(
            text="Jakey Bot v2.1.0 - DEGEN Edition | Page 2 of 3"
        )

        # Models Help Embed
        models_embed = discord.Embed(
            title="🤖 Jakey Bot - AI Models Guide",
            description="Available AI models for different tasks",
            color=discord.Color.purple(),
        )

        # AI Models
        models_embed.add_field(
            name="🤖 **AI Models Available**",
            value="• **Pollinations.AI Models** (Default - No API Key Required):\n - `pollinations::evil` - Uncensored responses\n - `pollinations::unity` - Uncensored with vision\n - `pollinations::openai` - Text generation\n  - `pollinations::openai-fast` - Fast text generation\n  - `pollinations::mistral` - Text generation",
            inline=False,
        )

        # AI Image Models
        models_embed.add_field(
            name="🎨 **Image Models Available**",
            value="• **Pollinations.AI Image Models**\n- `pollinations::flux` - Image generation\n- `pollinations::kontext` - Image-to-image\n- `pollinations::sdxl` - Image generation",
            inline=False,
        )

        # API Key Setup
        models_embed.add_field(
            name="🔑 **API Key Setup**",
            value="• **Pollinations.AI**: Some premium features may require API key\n• **Copy dev.env.template` to dev.env and add your keys",
            inline=False,
        )

        models_embed.set_footer(
            text="Jakey Bot v2.1.0 - DEGEN Edition | Page 3 of 3"
        )

        # Send all embeds
        await ctx.respond(
            embeds=[main_embed, commands_embed, models_embed], ephemeral=True
        )

    @commands.slash_command(
        name="quickstart",
        description="Get a quick start guide for Jakey Bot",
        guild_ids=None,  # Global command
    )
    async def quickstart(self, ctx):
        """Show quickstart guide"""
        embed = discord.Embed(
            title="🚀 Jakey The Degenerate Bot Quickstart Guide",
            description="Get up and running with Jakey The Degenerate Bot in 3 simple steps!",
            color=discord.Color.green(),
        )

        # Auto Tool Switch System - NEW FEATURE
        embed.add_field(
            name="🔄 **Auto Tool Switch System** ⭐ **NEW FEATURE**",
            value="**Just ask naturally** - JakeyBot automatically detects what tool you need!\n\n"
            "**Examples:**\n"
            "• `What's the price of Bitcoin?` → 🔄 **Auto-enabled CryptoPrice**\n"
            "• `Search for latest AI news` → 🔄 **Auto-enabled ExaSearch**\n"
            "• `Convert 100 USD to EUR` → 🔄 **Auto-enabled CurrencyConverter**\n\n"
            "**Key Benefits:**\n"
            "✅ **No Manual Tool Switching** - Tools enable automatically when needed\n"
            "✅ **Smart Timeout Management** - Tools return to Memory after optimal timeouts\n"
            "✅ **Intelligent Suggestions** - Get optimization tips with `/smart_suggestions`",
            inline=False,
        )

        # Step 1
        embed.add_field(
            name="1️⃣ Ask Your First Question",
            value="Just mention Jakey with your question!\n\n**Tools will auto-enable when needed!**",
            inline=False,
        )

        # Step 2
        embed.add_field(
            name="2️⃣ Explore AI Models",
            value="• Use `/model list` to see all available models\n• **Default Models** (No API Key Required):\n - `pollinations::evil` - Uncensored responses\n  - `pollinations::openai` - Text generation\n  - `pollinations::flux` - Image generation\n• Use `/model set <model>` to switch models (Admin only)",
            inline=False,
        )

        # Step 3
        embed.add_field(
            name="3️⃣ Use Advanced Features",
            value="• `/remind 1h take a break` - Set personal reminders\n• `/keno` - Generate keno numbers\n• `/generate_image <prompt>` - Generate images with Pollinations.AI\n• **Image Editing**: Use ImageGen tool with URL context\n• `/jakey_engage` - Make Jakey actively engage\n• `/create_bet` - Create betting pools\n• `/trivia` - Start trivia games\n• `/play <song>` - Play music in voice channels\n• `/sweep` - Clear conversation and reset",
            inline=False,
        )

        # Step 4
        embed.add_field(
            name="4️⃣ Use Smart Features",
            value="• `/smart_suggestions` - Get optimization tips\n• `/extend_timeout 5m` - Extend tool session time\n• `/timeout_status` - Check remaining time\n• `/auto_return_status` - View system overview",
            inline=False,
        )

        # Music quick reference
        embed.add_field(
            name="🎵 Music Commands (Quick)",
            value="• `/play <query>` - Start playback\n"
            "• `/skip` - Vote to skip\n"
            "• `/queue` - View upcoming tracks\n"
            "• `/nowplaying` - See current track\n"
            "• `/volume <0-100>` - Set volume\n"
            "• `/disconnect` - Leave voice channel\n\n"
            "More: use `/help` → Music Commands",
            inline=False,
        )

        # Common use cases
        embed.add_field(
            name="💭 What Can Jakey Do?",
            value="- Answer questions with AI intelligence\n- Remember your preferences and facts\n- Generate and edit images (direct commands)\n- Provide live crypto prices (auto-enabled)\n- Analyze YouTube videos (auto-enabled)\n- Help with coding and debugging (auto-enabled)\n- Create polls and trivia games\n- Generate keno numbers\n- Actively engage in channels\n\n*Note: Jakey is a degenerate bot, so he will be very rude and sarcastic. He will also be very helpful and will try to help you with your questions.*",
            inline=False,
        )

        embed.set_footer(
            text="Ready to get started? Tools auto-enable when you need them!"
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Misc(bot))
