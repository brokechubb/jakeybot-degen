#!/usr/bin/env python3
"""
Simple test script to verify slash commands are working
"""

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("dev.env")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ {bot.user} is ready!")

    # List all slash commands
    print("\n📋 Registered Slash Commands:")
    for command in bot.application_commands:
        print(f"  • /{command.name} - {command.description}")

    # Try to sync commands
    try:
        print("\n🔄 Syncing commands...")
        synced = await bot.sync_commands()
        print(f"✅ Synced {len(synced) if synced else 'all'} commands!")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

    # Exit after testing
    await bot.close()


# Load cogs
cogs_to_load = ["cogs.misc", "cogs.admin"]

for cog in cogs_to_load:
    try:
        bot.load_extension(cog)
        print(f"✅ Loaded {cog}")
    except Exception as e:
        print(f"❌ Failed to load {cog}: {e}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        print("❌ No TOKEN found in dev.env")
        exit(1)

    print("🚀 Starting command test...")
    bot.run(token)
