from discord.ext import commands
from discord import Member, DiscordException
from os import environ
import discord
import logging
import requests


class Misc(commands.Cog):
    """Use my other utilities here that can help make your server more active and entertaining"""

    def __init__(self, bot):
        self.bot = bot
        self.author = environ.get("BOT_NAME", "Jakey Bot")

    @commands.slash_command(
        name="help",
        aliases=["quickstart", "jakeyhelp"],
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

    @mimic.error
    async def on_command_error(self, ctx: commands.Context, error: DiscordException):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(
            error, commands.BadUnionArgument
        ):
            await ctx.respond(
                "⚠️ Please specify a valid discord user (or user id) and message to mimic!\n**Syntax:** `$mimic <user/user id> <message>`"
            )
        elif isinstance(error, commands.CommandInvokeError) or isinstance(
            error, commands.MissingPermissions
        ):
            await ctx.respond(
                "❌ Sorry, webhooks are not enabled in this channel. Please enable webhooks in this channel to use this command."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.respond(
                "❌ Sorry, this feature is not supported in DMs. Please use this command inside the guild."
            )
        elif isinstance(error, commands.ApplicationCommandInvokeError):
            await ctx.respond("⚠️ Please input a member")
        else:
            logging.error(
                "An error has occurred while executing mimic command, reason: ",
                exc_info=True,
            )


def setup(bot):
    bot.add_cog(Misc(bot))
