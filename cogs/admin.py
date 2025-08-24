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

    @commands.command(name="performance")
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
            if summary.get("slowest_commands"):
                slow_cmds = summary["slowest_commands"][:3]  # Top 3
                cmd_text = "\n".join(
                    [
                        f"• **{cmd['name']}**: {cmd['avg_time']:.3f}s avg ({cmd['total_calls']} calls, {cmd['error_rate']:.1%} errors)"
                        for cmd in slow_cmds
                    ]
                )
                embed.add_field(
                    name="🐌 Slowest Commands", value=cmd_text, inline=False
                )

            # API performance
            if summary.get("slowest_apis"):
                slow_apis = summary["slowest_apis"][:3]  # Top 3
                api_text = "\n".join(
                    [
                        f"• **{api['name']}**: {api['avg_time']:.3f}s avg ({api['total_calls']} calls, {api['error_rate']:.1%} errors)"
                        for api in slow_apis
                    ]
                )
                embed.add_field(name="🌐 Slowest APIs", value=api_text, inline=False)

            # Summary stats
            embed.add_field(
                name="📈 Summary",
                value=f"**Commands Monitored:** {summary.get('total_commands_monitored', 0)}\n"
                f"**APIs Monitored:** {summary.get('total_apis_monitored', 0)}\n"
                f"**DB Operations:** {summary.get('total_db_operations_monitored', 0)}",
                inline=False,
            )

            await ctx.send(embed=embed)

        except ImportError:
            await ctx.send("❌ Performance monitoring not available")
        except Exception as e:
            await ctx.send(f"❌ Error getting performance metrics: {e}")

    @commands.command(name="cache")
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

            await ctx.send(embed=embed)

        except ImportError:
            await ctx.send("❌ Cache manager not available")
        except Exception as e:
            await ctx.send(f"❌ Error getting cache stats: {e}")

    @commands.command(name="logs")
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

                await ctx.send(
                    "🎨 **Log Test Complete!** Check the console for colored output."
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

                await ctx.send(embed=embed)

            else:
                await ctx.send("❌ **Invalid action!** Use: `status` or `test`")

        except Exception as e:
            await ctx.send(f"❌ Error managing logs: {e}")

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
