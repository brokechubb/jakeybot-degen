import discord
from discord.ext import commands
import logging
import asyncio
import random

class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {} # To store channels where Jakey is actively participating
        self.bot.loop.create_task(self._monitor_channels())

    async def _monitor_channels(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, channel_id in self.active_channels.items():
                guild = self.bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        await self._interject_in_channel(channel)
            await asyncio.sleep(600) # Check every 10 minutes

    async def _interject_in_channel(self, channel: discord.TextChannel):
        # This is a placeholder for more sophisticated logic
        # For now, Jakey will just send a random in-character message
        messages = [
            "Yo, what's poppin' in here? Any degenerate plays goin' down? 🎰",
            "Rigged. Everything's rigged. But I'm still here, so what's your excuse? 💀",
            "Wen moon? Wen lambo? Wen CrashDaddy's BBQ? 🔥",
            "Don't tell CrashDaddy I said this, but y'all are lookin' broke today. EZ money for me. 💰",
            "Yard Life. Only the real ones know the pain. 🏈",
        ]
        if random.random() < 0.1: # 10% chance to interject
            await channel.send(random.choice(messages))
            logging.info(f"Jakey interjected in #{channel.name} ({channel.guild.name})")

    @commands.slash_command(name="jakey_engage", description="Make Jakey actively engage in the current channel.")
    @commands.has_permissions(manage_channels=True)
    async def jakey_engage(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_channels:
            await ctx.respond("Jakey is already engaging in a channel in this server. Use `/jakey_disengage` first.", ephemeral=True)
        else:
            self.active_channels[ctx.guild.id] = ctx.channel.id
            await ctx.respond(f"Yo, I'm officially in the mix in this channel, {ctx.channel.mention}! Let's get this bread. 🎰", ephemeral=False)
            logging.info(f"Jakey engagement activated in #{ctx.channel.name} ({ctx.guild.name})")

    @commands.slash_command(name="jakey_disengage", description="Stop Jakey from actively engaging in the current channel.")
    @commands.has_permissions(manage_channels=True)
    async def jakey_disengage(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_channels:
            del self.active_channels[ctx.guild.id]
            await ctx.respond(f"Alright, I'm out. Y'all can go back to being broke without my commentary. 💀", ephemeral=False)
            logging.info(f"Jakey engagement deactivated in #{ctx.channel.name} ({ctx.guild.name})")
        else:
            await ctx.respond("Jakey isn't actively engaging in any channel in this server.", ephemeral=True)

def setup(bot):
    bot.add_cog(Engagement(bot))
