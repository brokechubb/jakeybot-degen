import aiofiles
import aiofiles.os
import logging
import discord
import random
import subprocess
from discord.ext import commands
from os import environ
from datetime import datetime


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    # Shutdown command
    @commands.command(aliases=["exit", "stop", "quit", "shutdown"])
    @commands.is_owner()
    async def admin_shutdown(self, ctx):
        """Shuts down the bot"""
        await ctx.send("Shutting down...")
        await self.bot.close()

    @commands.slash_command(
        name="list_commands",
        description="List all registered slash commands (Owner only)",
        guild_ids=None,  # Global command
    )
    @commands.is_owner()
    async def list_commands(self, ctx):
        """List all registered slash commands."""
        try:
            await ctx.response.defer(ephemeral=True)

            commands_list = []
            for command in self.bot.application_commands:
                commands_list.append(f"• `/{command.name}` - {command.description}")

            if commands_list:
                embed = discord.Embed(
                    title="📋 Registered Slash Commands",
                    description="\n".join(commands_list),
                    color=discord.Color.green(),
                )
                embed.set_footer(text=f"Total: {len(commands_list)} commands")
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.respond("❌ No slash commands found!", ephemeral=True)

        except Exception as e:
            await ctx.respond(f"❌ Error listing commands: {str(e)}", ephemeral=True)

    @commands.slash_command(
        name="sync",
        description="Sync slash commands with Discord (Owner only)",
        guild_ids=None,  # Global command
    )
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Sync slash commands with Discord API."""
        try:
            await ctx.response.defer(ephemeral=True)

            # Simple sync approach for py-cord
            try:
                # Try to sync commands
                await self.bot.sync_commands()
                await ctx.respond(
                    "✅ Commands synced successfully! They should appear in 1-2 minutes.",
                    ephemeral=True,
                )
            except Exception as sync_error:
                logging.error(f"Sync error: {sync_error}")

                # Try alternative sync method
                try:
                    if hasattr(self.bot, "sync_all_application_commands"):
                        await self.bot.sync_all_application_commands()
                        await ctx.respond(
                            "✅ Commands synced using alternative method!",
                            ephemeral=True,
                        )
                    else:
                        raise sync_error
                except Exception as alt_error:
                    logging.error(f"Alternative sync failed: {alt_error}")
                    await ctx.respond(
                        f"❌ Sync failed: {str(sync_error)[:100]}...\n\n"
                        "Try restarting the bot instead.",
                        ephemeral=True,
                    )

        except Exception as e:
            logging.error(f"Sync command error: {e}")
            await ctx.respond(
                f"❌ Unexpected error: {str(e)[:100]}...",
                ephemeral=True,
            )

    @commands.slash_command(
        name="performance",
        description="View bot performance metrics (Admin only)",
        guild_ids=None,  # Global command
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def performance(self, ctx):
        """View bot performance metrics (Admin only)."""
        try:
            from core.services.performance_monitor import get_performance_summary

            summary = get_performance_summary()

            # Create performance report
            embed = discord.Embed(
                title="📊 Bot Performance Report",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )

            # System stats
            if summary.get("system"):
                sys = summary["system"]
                embed.add_field(
                    name="🖥️ System",
                    value=f"**Uptime:** {sys.get('uptime_formatted', 'Unknown')}\n"
                    f"**CPU:** {sys.get('current_cpu_percent', 0):.1f}% (avg: {sys.get('avg_cpu_percent_1h', 0):.1f}%)\n"
                    f"**Memory:** {sys.get('current_memory_percent', 0):.1f}% "
                    f"({sys.get('current_memory_used_gb', 0):.1f}GB / {sys.get('current_memory_total_gb', 0):.1f}GB)",
                    inline=False,
                )

            # Command performance
            if summary.get("commands"):
                cmd = summary["commands"]
                embed.add_field(
                    name="⚡ Commands",
                    value=f"**Total Commands:** {cmd.get('total_commands', 0)}\n"
                    f"**Avg Response Time:** {cmd.get('avg_response_time', 0):.2f}s\n"
                    f"**Commands/Minute:** {cmd.get('commands_per_minute', 0):.1f}",
                    inline=False,
                )

            # API usage
            if summary.get("api"):
                api = summary["api"]
                embed.add_field(
                    name="🌐 API Usage",
                    value=f"**Total Requests:** {api.get('total_requests', 0)}\n"
                    f"**Success Rate:** {api.get('success_rate', 0):.1%}\n"
                    f"**Avg Response Time:** {api.get('avg_response_time', 0):.2f}s",
                    inline=False,
                )

            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await ctx.respond(
                f"❌ Error getting performance metrics: {e}", ephemeral=True
            )

    @commands.slash_command(
        name="cache",
        description="View cache statistics (Admin only)",
        guild_ids=None,  # Global command
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def cache(self, ctx):
        """View cache statistics (Admin only)."""
        try:
            from core.services.cache_manager import cache_stats

            stats = cache_stats()

            embed = discord.Embed(
                title="💾 Cache Statistics",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )

            embed.add_field(
                name="📊 Cache Info",
                value=f"**Size:** {stats.get('size', 0)} / {stats.get('max_size', 0)}\n"
                f"**Hit Rate:** {stats.get('hit_rate', 0):.1%}\n"
                f"**Total Requests:** {stats.get('total_requests', 0)}",
                inline=False,
            )

            embed.add_field(
                name="📈 Performance",
                value=f"**Hits:** {stats.get('hits', 0)}\n"
                f"**Misses:** {stats.get('misses', 0)}\n"
                f"**Evictions:** {stats.get('evictions', 0)}\n"
                f"**Expirations:** {stats.get('expirations', 0)}",
                inline=False,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        except ImportError:
            await ctx.respond("❌ Cache manager not available", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error getting cache stats: {e}", ephemeral=True)

    @commands.slash_command(
        name="logs",
        description="View recent bot logs (Admin only)",
        guild_ids=None,  # Global command
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx, action: str = "status"):
        """Manage colored logging (Admin only). Actions: status, test"""
        try:
            if action.lower() == "test":
                # Test all log levels
                from core.services.colored_logging import (
                    log_success,
                    log_info,
                    log_warning,
                    log_error,
                    log_debug,
                )

                log_debug("Debug test message")
                log_info("Info test message")
                log_success("Success test message")
                log_warning("Warning test message")
                log_error("Error test message")

                await ctx.respond(
                    "🎨 **Log Test Complete!** Check the console for colored output.",
                    ephemeral=True,
                )

            elif action.lower() == "status":
                import sys

                # Check if colors are supported
                color_support = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

                embed = discord.Embed(
                    title="🎨 Logging Status",
                    color=discord.Color.purple(),
                    timestamp=datetime.now(),
                )

                embed.add_field(
                    name="📊 Status",
                    value=f"**Color Support:** {'✅ Enabled' if color_support else '❌ Disabled'}\n"
                    f"**Terminal:** {'✅ TTY' if color_support else '❌ Non-TTY'}\n"
                    f"**Logging Level:** {logging.getLogger().level}",
                    inline=False,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            else:
                await ctx.respond(
                    "❌ **Invalid action!** Use: `status` or `test`", ephemeral=True
                )

        except Exception as e:
            await ctx.respond(f"❌ Error managing logs: {e}", ephemeral=True)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("❌ Sorry, only the owner can use this command.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond(
                f"❌ You are missing the required permissions to use this command. Needed permissions:\n```{error}```"
            )
        else:
            raise error


def setup(bot):
    bot.add_cog(Admin(bot))
