import logging
import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from core.ai.history import History


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    # Shutdown command
    @commands.slash_command(
        name="shutdown",
        description="Shut down the bot (Owner only)",
        guild_ids=None,  # Global command
    )
    @commands.is_owner()
    async def admin_shutdown(self, ctx):
        """Shuts down the bot"""
        await ctx.respond("Shutting down...", ephemeral=True)
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

            # Sync commands using py-cord
            try:
                await self.bot.sync_commands()
                await ctx.respond(
                    "✅ Commands synced successfully! They should appear in 1-2 minutes.",
                    ephemeral=True,
                )
            except Exception as sync_error:
                logging.error(f"Sync error: {sync_error}")
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
    async def logs(self, ctx, log_type: str = "out", lines: int = 20):
        """View recent bot logs (Admin only). Types: out, error"""
        try:
            await ctx.response.defer(ephemeral=True)
            
            # Validate log type
            if log_type.lower() not in ["out", "error"]:
                await ctx.respond(
                    "❌ **Invalid log type!** Use: `out` or `error`", ephemeral=True
                )
                return

            # Determine log file path
            if log_type.lower() == "out":
                log_file = "/home/chubb/.pm2/logs/jakey-out.log"
                title = "📝 Bot Output Logs"
                color = discord.Color.blue()
            else:
                log_file = "/home/chubb/.pm2/logs/jakey-error.log"
                title = "🚨 Bot Error Logs"
                color = discord.Color.red()

            # Check if file exists
            import os
            if not os.path.exists(log_file):
                await ctx.respond(
                    f"❌ **Log file not found:** {log_file}", ephemeral=True
                )
                return

            # Read last N lines from log file
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read all lines and get last N lines
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
                    
                    if not recent_lines:
                        log_content = "📝 *No log entries found*"
                    else:
                        log_content = "```ansi\n" + ''.join(recent_lines) + "```"
                        
                        # Truncate if too long for Discord (4000 chars limit)
                        if len(log_content) > 4000:
                            log_content = log_content[:3900] + "\n```... [truncated]```"
            except Exception as e:
                await ctx.respond(
                    f"❌ **Error reading log file:** {str(e)}", ephemeral=True
                )
                return

            # Create embed with log content
            embed = discord.Embed(
                title=title,
                description=f"**Showing last {len(recent_lines)} lines**\n{log_content}",
                color=color,
                timestamp=datetime.now(),
            )

            embed.add_field(
                name="📁 File",
                value=f"`{log_file}`",
                inline=False
            )

            embed.add_field(
                name="⚙️ Options",
                value=f"Use `/logs type: error` for error logs\n"
                      f"Use `/logs lines: 50` for more lines",
                inline=False
            )

            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await ctx.respond(f"❌ Error viewing logs: {e}", ephemeral=True)

    @commands.slash_command(
        name="inject_fact",
        description="Inject important facts into the global knowledge base (Owner only)",
        guild_ids=None,  # Global command
    )
    @commands.is_owner()
    async def inject_fact(
        self,
        ctx,
        fact: str,
        category: str = "global",
        expires_in: str = "never",
        make_public: bool = True,
    ):
        """
        Inject important facts into the global knowledge base.
        
        Args:
            fact: The fact or information to remember
            category: Category for organizing the fact (default: "global")
            expires_in: Expiration time (e.g., '1d', '2h', '30m', 'never' for permanent)
            make_public: Whether the fact should be accessible to all users (default: True)
        """
        try:
            await ctx.response.defer(ephemeral=True)

            # Validate that we have a database connection
            if not hasattr(self.bot, "DBConn") or not self.bot.DBConn:
                await ctx.respond(
                    "❌ Database connection not available", ephemeral=True
                )
                return

            history_db = self.bot.DBConn

            # Parse expiration time
            expires_at = None
            if expires_in and expires_in.lower() != "never":
                try:
                    now = datetime.now(timezone.utc)
                    if expires_in.endswith("d"):
                        days = int(expires_in[:-1])
                        expires_at = now + timedelta(days=days)
                    elif expires_in.endswith("h"):
                        hours = int(expires_in[:-1])
                        expires_at = now + timedelta(hours=hours)
                    elif expires_in.endswith("m"):
                        minutes = int(expires_in[:-1])
                        expires_at = now + timedelta(minutes=minutes)
                    else:
                        raise ValueError("Invalid time format")
                except:
                    await ctx.respond(
                        "⚠️ Invalid expiration format. Use number followed by d, h, or m (e.g., 1d, 2h, 30m), or 'never' for permanent",
                        ephemeral=True,
                    )
                    return

            # Determine target guild/user ID for global facts
            # For global facts, we'll use a special system-wide identifier
            guild_id = 0  # Special ID for global facts
            user_id = ctx.author.id

            # Prepend system indicator to fact text
            system_prefix = "[SYSTEM_GLOBAL]" if make_public else "[SYSTEM_PRIVATE]"
            category_prefix = f"[{category}]" if category else ""
            fact_with_metadata = f"{system_prefix}{category_prefix} {fact}"

            # Store the fact in the global knowledge base
            fact_id = await history_db.add_fact(
                guild_id=guild_id,
                user_id=user_id,
                fact_text=fact_with_metadata,
                source=f"admin_injection/{user_id}",
                expires_at=expires_at,
            )

            # Prepare response
            response = f"✅ Successfully injected fact into global knowledge base:\n**{fact}**"
            if category:
                response += f"\n📁 Category: {category}"
            if expires_at:
                response += f"\n⏰ Expires: {expires_at.strftime('%Y-%m-%d %H:%M')} UTC"
            else:
                response += "\n♾️ Permanent"

            await ctx.respond(response, ephemeral=True)

        except Exception as e:
            logging.error(f"Error injecting fact: {e}")
            await ctx.respond(
                f"❌ Failed to inject fact: {str(e)}", ephemeral=True
            )

    @commands.slash_command(
        name="list_global_facts",
        description="List all global facts in the knowledge base (Owner only)",
        guild_ids=None,  # Global command
    )
    @commands.is_owner()
    async def list_global_facts(self, ctx, limit: int = 10):
        """List all global facts in the knowledge base."""
        try:
            await ctx.response.defer(ephemeral=True)

            # Validate that we have a database connection
            if not hasattr(self.bot, "DBConn") or not self.bot.DBConn:
                await ctx.respond(
                    "❌ Database connection not available", ephemeral=True
                )
                return

            history_db = self.bot.DBConn

            # Limit the results
            limit = min(max(1, limit), 50)

            # Get global facts (guild_id = 0)
            guild_id = 0
            collection_name = f"knowledge_{guild_id}"

            # Check if collection exists
            collections = await history_db._db.list_collection_names()
            if collection_name not in collections:
                await ctx.respond("📝 No global facts found in the knowledge base.", ephemeral=True)
                return

            knowledge_collection = history_db._db[collection_name]
            facts = []

            try:
                async for fact in knowledge_collection.find().sort("created_at", -1).limit(limit):
                    if fact and (
                        fact.get("expires_at") is None
                        or fact["expires_at"] > datetime.now(timezone.utc)
                    ):
                        facts.append(fact)

                if not facts:
                    await ctx.respond("📝 No global facts found in the knowledge base.", ephemeral=True)
                    return

                # Format the response
                embed = discord.Embed(
                    title="🌍 Global Knowledge Base Facts",
                    color=discord.Color.gold(),
                    timestamp=datetime.now(),
                )

                for i, fact in enumerate(facts, 1):
                    fact_text = fact.get("fact_text", "Unknown fact")
                    created_at = fact.get("created_at", datetime.now(timezone.utc))
                    expires_at = fact.get("expires_at")
                    
                    # Clean up the fact text for display
                    display_text = fact_text.replace("[SYSTEM_GLOBAL]", "").replace("[SYSTEM_PRIVATE]", "")
                    
                    field_value = f"**{display_text}**"
                    if expires_at:
                        field_value += f"\n*Expires: {expires_at.strftime('%Y-%m-%d %H:%M')}*"
                    field_value += f"\n*Added: {created_at.strftime('%Y-%m-%d %H:%M')}*"
                    
                    embed.add_field(
                        name=f"Fact #{i}",
                        value=field_value,
                        inline=False
                    )

                embed.set_footer(text=f"Showing {len(facts)} of {limit} facts")

                await ctx.respond(embed=embed, ephemeral=True)

            except Exception as e:
                logging.error(f"Error listing global facts: {e}")
                await ctx.respond(f"❌ Failed to list global facts: {str(e)}", ephemeral=True)

        except Exception as e:
            logging.error(f"Error in list_global_facts: {e}")
            await ctx.respond(f"❌ Error: {str(e)}", ephemeral=True)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("❌ Sorry, only the owner can use this command.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond(
                f"❌ You are missing the required permissions to use this command. Needed permissions:\n```{error}```"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = int(error.retry_after)
            await ctx.respond(f"⏰ **Cooldown**: Try again in {retry_after} seconds.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Admin(bot))
