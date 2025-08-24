import logging
import discord
from discord.ext import commands
import asyncio
import random
import yaml
import os
from datetime import datetime, timedelta
from core.services.database_manager import DatabaseManager


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {}  # To store channels where Jakey is actively participating
        self.last_message_times = {}  # Track when Jakey last messaged in each channel
        self.config = self._load_config()
        self.db_manager = DatabaseManager()
        self.bot.loop.create_task(self._load_persistent_data())
        self.bot.loop.create_task(self._monitor_channels())
        self.bot.loop.create_task(self._cleanup_invalid_channels())

    def _load_config(self):
        """Load engagement configuration from YAML file."""
        config_path = "data/engagement_config.yaml"
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as file:
                    return yaml.safe_load(file)
            else:
                logging.warning(
                    f"Engagement config file not found at {config_path}, using defaults"
                )
                return self._get_default_config()
        except Exception as e:
            logging.error(f"Failed to load engagement config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self):
        """Return default configuration if config file is not available."""
        return {
            "engagement": {
                "check_interval": 600,
                "interjection_probability": 0.1,
                "max_channels": 50,
                "min_interval_between_messages": 300,
                "enable_logging": True,
                "enable_persistence": True,
            },
            "database": {
                "collection_name": "engagement_settings",
                "auto_cleanup": True,
                "cleanup_interval": 3600,
            },
            "permissions": {
                "engage_required": "manage_channels",
                "list_required": "manage_guild",
                "allow_multiple_channels": False,
            },
        }

    async def _load_persistent_data(self):
        """Load persistent engagement data from database on startup."""
        await self.bot.wait_until_ready()
        if not self.config["engagement"]["enable_persistence"]:
            logging.info("Engagement persistence is disabled")
            return

        try:
            db = await self.db_manager.get_database()
            collection = db[self.config["database"]["collection_name"]]

            # Load all engagement settings
            async for doc in collection.find({}):
                guild_id = doc.get("guild_id")
                channel_id = doc.get("channel_id")
                if guild_id and channel_id:
                    self.active_channels[guild_id] = channel_id
                    logging.info(
                        f"Loaded persistent engagement for guild {guild_id} in channel {channel_id}"
                    )

            logging.info(
                f"Loaded {len(self.active_channels)} persistent engagement settings"
            )
        except Exception as e:
            logging.error(f"Failed to load persistent engagement data: {e}")

    async def _save_engagement_data(self, guild_id: int, channel_id: int, action: str):
        """Save engagement data to database."""
        if not self.config["engagement"]["enable_persistence"]:
            return

        try:
            db = await self.db_manager.get_database()
            collection = db[self.config["database"]["collection_name"]]

            if action == "engage":
                # Save engagement setting
                await collection.update_one(
                    {"guild_id": guild_id},
                    {
                        "$set": {
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "engaged_at": datetime.utcnow(),
                            "engaged_by": "system",
                        }
                    },
                    upsert=True,
                )
                if self.config["engagement"]["enable_logging"]:
                    logging.info(
                        f"Saved engagement setting for guild {guild_id} in channel {channel_id}"
                    )
            elif action == "disengage":
                # Remove engagement setting
                await collection.delete_one({"guild_id": guild_id})
                if self.config["engagement"]["enable_logging"]:
                    logging.info(f"Removed engagement setting for guild {guild_id}")
        except Exception as e:
            logging.error(f"Failed to save engagement data: {e}")

    async def _cleanup_invalid_channels(self):
        """Periodically clean up invalid channels and guilds."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.config["database"]["auto_cleanup"]:
                await self._perform_cleanup()
            await asyncio.sleep(self.config["database"]["cleanup_interval"])

    async def _perform_cleanup(self):
        """Remove invalid channels and guilds from active engagement list."""
        channels_to_remove = []

        for guild_id, channel_id in self.active_channels.items():
            guild = self.bot.get_guild(guild_id)
            if not guild:
                channels_to_remove.append(guild_id)
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                channels_to_remove.append(guild_id)
                continue

        # Remove invalid channels
        for guild_id in channels_to_remove:
            del self.active_channels[guild_id]
            if self.config["engagement"]["enable_logging"]:
                logging.info(f"Cleaned up invalid engagement for guild {guild_id}")

        if channels_to_remove:
            logging.info(
                f"Cleaned up {len(channels_to_remove)} invalid engagement settings"
            )

    async def _monitor_channels(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, channel_id in self.active_channels.items():
                guild = self.bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        await self._interject_in_channel(channel)

            await asyncio.sleep(self.config["engagement"]["check_interval"])

    async def _interject_in_channel(self, channel: discord.TextChannel):
        """Send a random interjection message to the channel if conditions are met."""
        # Check if enough time has passed since last message
        current_time = datetime.utcnow()
        last_time = self.last_message_times.get(channel.id)

        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < self.config["engagement"]["min_interval_between_messages"]:
                return  # Too soon to message again

        # Check probability for interjection
        if random.random() < self.config["engagement"]["interjection_probability"]:
            try:
                message = random.choice(
                    self.config.get("messages", self._get_default_messages())
                )
                await channel.send(message)

                # Update last message time
                self.last_message_times[channel.id] = current_time

                if self.config["engagement"]["enable_logging"]:
                    logging.info(
                        f"Jakey interjected in #{channel.name} ({channel.guild.name})"
                    )
            except discord.Forbidden:
                logging.warning(
                    f"Jakey doesn't have permission to send messages in #{channel.name}"
                )
            except Exception as e:
                logging.error(
                    f"Failed to send engagement message in #{channel.name}: {e}"
                )

    def _get_default_messages(self):
        """Return default messages if config is not available."""
        return [
            "Yo, what's poppin' in here? Any degenerate plays goin' down? 🎰",
            "Rigged. Everything's rigged. But I'm still here, so what's your excuse? 💀",
            "Wen moon? Wen lambo? Wen CrashDaddy's BBQ? 🔥",
            "Don't tell CrashDaddy I said this, but y'all are lookin' broke today. EZ money for me. 💰",
            "Yard Life. Only the real ones know the pain. 🏈",
        ]

    @commands.slash_command(
        name="jakey_engage",
        description="Make Jakey actively engage in the current channel.",
    )
    @commands.has_permissions(manage_channels=True)
    async def jakey_engage(self, ctx: discord.ApplicationContext):
        # Check if already engaging in this guild
        if ctx.guild.id in self.active_channels:
            await ctx.respond(
                "Jakey is already engaging in a channel in this server. Use `/jakey_disengage` first.",
                ephemeral=True,
            )
            return

        # Check maximum channel limit
        if len(self.active_channels) >= self.config["engagement"]["max_channels"]:
            await ctx.respond(
                "Jakey is already engaging in the maximum number of channels. Disengage from another server first.",
                ephemeral=True,
            )
            return

        # Add channel to active engagement
        self.active_channels[ctx.guild.id] = ctx.channel.id
        await self._save_engagement_data(ctx.guild.id, ctx.channel.id, "engage")

        await ctx.respond(
            f"Yo, I'm officially in the mix in this channel, {ctx.channel.mention}! Let's get this bread. 🎰",
            ephemeral=False,
        )

        if self.config["engagement"]["enable_logging"]:
            logging.info(
                f"Jakey engagement activated in #{ctx.channel.name} ({ctx.guild.name})"
            )

    @commands.slash_command(
        name="jakey_disengage",
        description="Stop Jakey from actively engaging in the current channel.",
    )
    @commands.has_permissions(manage_channels=True)
    async def jakey_disengage(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_channels:
            del self.active_channels[ctx.guild.id]
            await self._save_engagement_data(ctx.guild.id, ctx.channel.id, "disengage")
            await ctx.respond(
                f"Alright, I'm out. Y'all can go back to being broke without my commentary. 💀",
                ephemeral=False,
            )

            if self.config["engagement"]["enable_logging"]:
                logging.info(
                    f"Jakey engagement deactivated in #{ctx.channel.name} ({ctx.guild.name})"
                )
        else:
            await ctx.respond(
                "Jakey isn't actively engaging in any channel in this server.",
                ephemeral=True,
            )

    @commands.slash_command(
        name="jakey_engagement_status",
        description="Check Jakey's current engagement status.",
    )
    async def jakey_engagement_status(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_channels:
            channel_id = self.active_channels[ctx.guild.id]
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await ctx.respond(
                    f"Jakey is actively engaging in {channel.mention} in this server. 🎰",
                    ephemeral=True,
                )
            else:
                await ctx.respond(
                    "Jakey's engagement channel no longer exists. Use `/jakey_disengage` to clean up.",
                    ephemeral=True,
                )
        else:
            await ctx.respond(
                "Jakey isn't actively engaging in any channel in this server.",
                ephemeral=True,
            )

    @commands.slash_command(
        name="jakey_engagement_list",
        description="List all servers where Jakey is actively engaging.",
    )
    @commands.has_permissions(manage_guild=True)
    async def jakey_engagement_list(self, ctx: discord.ApplicationContext):
        if not self.active_channels:
            await ctx.respond(
                "Jakey isn't actively engaging in any servers right now.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🎰 Jakey's Active Engagements",
            description=f"Servers where Jakey is actively participating ({len(self.active_channels)} total):",
            color=0x00FF00,
            timestamp=datetime.utcnow(),
        )

        for guild_id, channel_id in self.active_channels.items():
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    embed.add_field(
                        name=f"🏠 {guild.name}",
                        value=f"Channel: {channel.mention}\nID: {guild_id}",
                        inline=False,
                    )

        embed.set_footer(text=f"Total active engagements: {len(self.active_channels)}")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="jakey_engagement_stats",
        description="View engagement statistics and configuration.",
    )
    @commands.has_permissions(manage_guild=True)
    async def jakey_engagement_stats(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="📊 Jakey Engagement Statistics",
            color=0x0099FF,
            timestamp=datetime.utcnow(),
        )

        # Current engagement stats
        embed.add_field(
            name="🎯 Current Status",
            value=f"Active channels: {len(self.active_channels)}\nMax allowed: {self.config['engagement']['max_channels']}",
            inline=True,
        )

        # Configuration info
        embed.add_field(
            name="⚙️ Configuration",
            value=f"Check interval: {self.config['engagement']['check_interval']}s\nInterjection chance: {self.config['engagement']['interjection_probability'] * 100}%",
            inline=True,
        )

        # Database info
        embed.add_field(
            name="🗄️ Database",
            value=f"Persistence: {'Enabled' if self.config['engagement']['enable_persistence'] else 'Disabled'}\nAuto-cleanup: {'Enabled' if self.config['database']['auto_cleanup'] else 'Disabled'}",
            inline=True,
        )

        embed.set_footer(
            text="Use /jakey_engagement_list to see all active engagements"
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Engagement(bot))
