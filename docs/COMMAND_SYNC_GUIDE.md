# 🔧 Discord Slash Command Sync Guide

This guide explains how to sync the new slash commands with Discord so they appear in your server.

## 🚨 **Important**: Commands Need to be Synced

After adding new slash commands, they need to be registered with Discord's API before they appear in your server. This is a one-time process.

## 🔄 **How to Sync Commands**

### Method 1: Automatic Sync (Recommended)

1. **Start the bot** and wait for it to fully load
2. **Check the logs** - you should see:

   ```
   ✅ Slash commands synced successfully!
   ```

3. **Wait 1-2 minutes** for Discord to process the changes

### Method 2: Use the Sync Command (Manual)

1. **Start the bot** and wait for it to fully load
2. **Run the sync command** (requires bot owner permissions):

   ```
   /sync
   ```

3. **Wait for confirmation** - you should see a message like:

   ```
   ✅ Commands synced successfully! They should appear in 1-2 minutes.
   ```

### Method 2: Restart the Bot

1. **Stop the bot** (Ctrl+C or kill the process)
2. **Wait 10-15 seconds** for Discord to process the changes
3. **Restart the bot**:

   ```bash
   python main.py
   ```

4. **Wait for full startup** - commands should appear automatically

### Method 3: Manual Sync (Advanced)

If the above methods don't work, you can manually sync commands:

```python
# In a Python console or script
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
# ... bot setup ...

@bot.event
async def on_ready():
    print("Syncing commands...")
    await bot.sync_commands()
    print("Commands synced!")

bot.run('YOUR_TOKEN')
```

## 📋 **New Commands Added**

The following new commands have been added and need syncing:

### 🎨 **Image Generation Commands**

- `/generate_image` - Generate images with Gemini AI
- `/generate_pollinations` - Generate images with Pollinations.AI
- `/edit_image` - Edit existing images
- `/image_help` - Show image generation help

### 🤖 **Auto-Image Commands**

- `/auto_image` - Toggle automatic image generation
- `/auto_image_status` - Check auto-image status
- `/auto_image_debug` - Debug auto-image system

### ⚙️ **Admin Commands**

- `/performance` - View bot performance metrics
- `/cache` - View cache statistics
- `/logs` - View recent bot logs
- `/sync` - Sync commands with Discord

### 🧠 **Memory Commands**

- `/memory_debug` - Debug memory system
- `/memory_reindex` - Reindex memory system

### ⏰ **Timeout Commands**

- `/timeout_status` - Check tool timeout status
- `/extend_timeout` - Extend current tool timeout
- `/return_to_default` - Return to default tool
- `/auto_return_status` - Check auto-return system status

## 🔍 **Verification Steps**

After syncing, verify the commands work:

1. **Check command list**: Type `/` in Discord and look for the new commands
2. **Test basic commands**:

   ```
   /help
   /auto_image_status
   /image_help
   ```

3. **Test admin commands** (if you have permissions):

   ```
   /performance
   /cache
   /auto_image_debug
   ```

## 🚨 **Common Issues**

### Issue: Commands Not Appearing

**Solution**:

- Wait 1-2 minutes after syncing
- Restart Discord client
- Check bot permissions in server

### Issue: "Unknown Command" Error

**Solution**:

- Run `/sync` again
- Restart the bot
- Check bot logs for errors

### Issue: Permission Denied

**Solution**:

- Ensure bot has "Use Slash Commands" permission
- Check if you have admin/owner permissions for sync command

### Issue: Sync Command Not Working

**Solution**:

- Ensure you're the bot owner
- Check bot logs for sync errors
- Try restarting the bot

### Issue: "object of type 'NoneType' has no len()"

**Problem**: The sync command returns `None` instead of a list of commands.

**Solution**:

- This is a py-cord version compatibility issue
- The bot now automatically syncs commands on startup
- Try restarting the bot instead of using `/sync`
- Check bot logs for sync status on startup

## 📝 **Bot Permissions Required**

Make sure the bot has these permissions in your server:

- ✅ **Use Slash Commands**
- ✅ **Send Messages**
- ✅ **Embed Links**
- ✅ **Attach Files** (for image generation)
- ✅ **Manage Messages** (for admin commands)

## 🔧 **Troubleshooting**

### Check Bot Logs

Look for these messages in the bot logs:

```
✅ Commands synced successfully
❌ Failed to sync commands: [error]
```

### Force Global Sync

If guild-specific sync isn't working, you can force a global sync by restarting the bot multiple times.

### Discord API Limits

Discord has rate limits for command syncing. If you get rate limited:

- Wait 1-2 minutes between sync attempts
- Don't restart the bot repeatedly

## 📞 **Getting Help**

If commands still don't appear after following this guide:

1. **Check bot logs** for error messages
2. **Verify bot permissions** in your server
3. **Try the sync command** multiple times
4. **Restart both bot and Discord client**
5. **Contact support** with:
   - Bot logs
   - Sync command output
   - Server permissions screenshot

---

**Remember**: Slash commands can take up to 1 hour to appear globally, but usually appear within 1-2 minutes after syncing.
