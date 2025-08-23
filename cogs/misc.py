from discord.ext import commands
from discord import Member, DiscordException
from os import environ
import discord
import logging
import requests
import datetime
import time
import asyncio
import re
import motor.motor_asyncio
from core.ai.history import History


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

    def _parse_time_input(self, time_input: str) -> datetime.datetime:
        now = datetime.datetime.now()
        time_input = time_input.lower()

        if time_input.endswith("m"):
            minutes = int(time_input[:-1])
            return now + datetime.timedelta(minutes=minutes)
        elif time_input.endswith("h"):
            hours = int(time_input[:-1])
            return now + datetime.timedelta(hours=hours)
        elif time_input.endswith("d"):
            days = int(time_input[:-1])
            return now + datetime.timedelta(days=days)
        elif "tomorrow" in time_input:
            tomorrow = now + datetime.timedelta(days=1)
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
                target_time += datetime.timedelta(days=1)
            return target_time

        return None

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
        now = datetime.datetime.now()
        dst_status = "active" if time.localtime().tm_isdst else "inactive"
        await ctx.respond(
            f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}. Daylight Saving Time is currently {dst_status}."
        )

    @commands.command(
        name="time", description="Displays the current time and DST status."
    )
    async def current_time_prefix(self, ctx):
        """Displays the current time and DST status."""
        now = datetime.datetime.now()
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
        name="quickstart",
        description="Display the JakeyBot Quickstart Guide",
        contexts={discord.InteractionContextType.guild},
        integration_types={discord.IntegrationType.guild_install},
    )
    async def jakey_help_slash(self, ctx):
        """Display the JakeyBot Quickstart Guide"""
        await self._send_help_guide(ctx)

    @commands.command(
        name="help", aliases=["quickstart", "jakeyhelp", "HELP", "QUICKSTART"]
    )
    async def jakey_help_prefix(self, ctx):
        """Display the JakeyBot Quickstart Guide"""
        await self._send_help_guide(ctx)

    async def _send_help_guide(self, ctx):
        """Helper method to send the help guide (used by both slash and prefix commands)"""
        # The raw GitHub URL for the file
        md_url = "https://raw.githubusercontent.com/brokechubb/JakeyBot/refs/heads/master/docs/DISCORD_QUICKSTART.md"

        try:
            # Fetch the raw Markdown content from GitHub
            response = requests.get(md_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            markdown_content = response.text

            # Convert Markdown to Discord markdown format
            discord_formatted_text = ""
            in_code_block = False
            code_language = ""

            for line in markdown_content.split("\n"):
                # Handle code blocks
                if line.startswith("```"):
                    if not in_code_block:
                        # Starting a code block
                        in_code_block = True
                        code_language = line[3:].strip()  # Get language identifier
                        discord_formatted_text += f"```{code_language}\n"
                    else:
                        # Ending a code block
                        in_code_block = False
                        discord_formatted_text += "```\n"
                    continue

                if in_code_block:
                    # Inside code block, preserve formatting
                    discord_formatted_text += line + "\n"
                    continue

                # Handle headers
                if line.startswith("# "):
                    discord_formatted_text += f"**{line[2:].strip()}**\n"
                elif line.startswith("## "):
                    discord_formatted_text += f"**{line[3:].strip()}**\n"
                elif line.startswith("### "):
                    discord_formatted_text += f"**{line[4:].strip()}**\n"
                elif line.startswith("#### "):
                    discord_formatted_text += f"**{line[5:].strip()}**\n"
                elif line.startswith("##### "):
                    discord_formatted_text += f"**{line[6:].strip()}**\n"
                elif line.startswith("###### "):
                    discord_formatted_text += f"**{line[7:].strip()}**\n"

                # Handle bold text (**text** or __text__)
                elif "**" in line or "__" in line:
                    # Preserve existing bold formatting
                    discord_formatted_text += line + "\n"

                # Handle italic text (*text* or _text_)
                elif "*" in line or "_" in line:
                    # Preserve existing italic formatting
                    discord_formatted_text += line + "\n"

                # Handle inline code (`code`)
                elif "`" in line:
                    # Preserve existing inline code formatting
                    discord_formatted_text += line + "\n"

                # Handle links [text](url)
                elif "[" in line and "](" in line and ")" in line:
                    # Preserve existing link formatting
                    discord_formatted_text += line + "\n"

                # Handle lists
                elif line.strip().startswith("- "):
                    discord_formatted_text += line + "\n"
                elif line.strip().startswith("* "):
                    discord_formatted_text += line + "\n"
                elif line.strip().startswith("1. "):
                    discord_formatted_text += line + "\n"

                # Handle blockquotes
                elif line.strip().startswith(">"):
                    discord_formatted_text += line + "\n"

                # Handle horizontal rules
                elif line.strip() in ["---", "***", "___"]:
                    discord_formatted_text += (
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    )

                # Handle empty lines
                elif line.strip() == "":
                    discord_formatted_text += "\n"

                # Regular text
                else:
                    discord_formatted_text += line + "\n"

            # Split content into chunks to handle Discord's 4096 character limit
            max_length = 4000  # Leave some buffer for safety
            chunks = []
            current_chunk = ""

            for line in discord_formatted_text.split("\n"):
                if len(current_chunk) + len(line) + 1 > max_length:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Send the first chunk as an embed
            if chunks:
                embed = discord.Embed(
                    title="JakeyBot Quickstart Guide",
                    description=chunks[0],
                    url=md_url,  # Link back to the original GitHub file
                    color=0x3498DB,  # Customize the color
                )
                embed.set_footer(
                    text=f"Page 1 of {len(chunks)} • Use the link above to view the full guide"
                )

                # Handle both slash and prefix command responses
                if hasattr(ctx, "respond"):
                    # Slash command
                    await ctx.respond(embed=embed)
                else:
                    # Prefix command
                    await ctx.send(embed=embed)

                # Send remaining chunks as additional embeds
                for i, chunk in enumerate(chunks[1:], 2):
                    embed = discord.Embed(
                        title=f"JakeyBot Quickstart Guide (Continued)",
                        description=chunk,
                        url=md_url,
                        color=0x3498DB,
                    )
                    embed.set_footer(
                        text=f"Page {i} of {len(chunks)} • Use the link above to view the full guide"
                    )

                    # Handle both slash and prefix command responses
                    if hasattr(ctx, "followup"):
                        # Slash command
                        await ctx.followup.send(embed=embed)
                    else:
                        # Prefix command
                        await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching the Markdown file: {e}"
            if hasattr(ctx, "respond"):
                await ctx.respond(error_msg)
            else:
                await ctx.send(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            if hasattr(ctx, "respond"):
                await ctx.respond(error_msg)
            else:
                await ctx.send(error_msg)

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


def setup(bot):
    bot.add_cog(Misc(bot))
