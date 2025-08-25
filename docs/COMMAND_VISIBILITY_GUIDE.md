# 🔍 Discord Command Visibility Troubleshooting

If the slash commands are not appearing in Discord, follow this guide to diagnose and fix the issue.

## ✅ **Commands Are Working!**

The test script confirms that **all 24 slash commands are properly registered**:

- 🎨 Image Generation: `/generate_image`, `/generate_pollinations`, `/edit_image`, `/image_help`
- 🤖 Auto-Image: `/auto_image`, `/auto_image_status`, `/auto_image_debug`
- ⚙️ Admin: `/performance`, `/cache`, `/logs`, `/sync`, `/list_commands`
- 🧠 Memory: `/memory_debug`, `/memory_reindex`
- ⏰ Timeout: `/timeout_status`, `/extend_timeout`, `/return_to_default`
- 📋 General: `/help`, `/quickstart`, `/time`, `/remind`, `/mimic`

## 🚨 **Why Commands Might Not Appear**

### 1. **Discord UI Delay**

- **Problem**: Discord can take 1-60 minutes to show new commands
- **Solution**: Wait 1-2 minutes, then refresh Discord or restart the Discord client

### 2. **Bot Permissions**

- **Problem**: Bot lacks required permissions
- **Solution**: Ensure bot has these permissions in your server:
  - ✅ **Use Slash Commands**
  - ✅ **Send Messages**
  - ✅ **Embed Links**
  - ✅ **Attach Files**

### 3. **Server-Specific Issues**

- **Problem**: Commands only work in certain servers
- **Solution**: Check if bot is properly added to your server with correct permissions

### 4. **Discord Client Cache**

- **Problem**: Discord client has cached old command list
- **Solution**:
  - Restart Discord client
  - Clear Discord cache
  - Try on mobile Discord app

## 🔧 **Diagnostic Steps**

### Step 1: Check Bot Status

```
/list_commands
```

This will show all registered commands (owner only).

### Step 2: Test Basic Commands

Try these commands that should always work:

```
/help
/time
```

### Step 3: Check Bot Permissions

1. Go to Server Settings → Integrations → Bots and Apps
2. Find your bot and check permissions
3. Ensure "Use Slash Commands" is enabled

### Step 4: Force Refresh

1. **Restart Discord client**
2. **Wait 2-3 minutes**
3. **Try typing `/` and see if commands appear**

## 🎯 **Quick Fixes**

### Fix 1: Restart Everything

```bash
# Stop the bot
pkill -f "python main.py"

# Wait 10 seconds
sleep 10

# Restart the bot
python main.py

# Restart Discord client
```

### Fix 2: Check Bot Logs

Look for these messages in bot logs:

```
✅ Slash commands synced successfully!
```

### Fix 3: Test in Different Server

Try the commands in a different Discord server to see if it's server-specific.

### Fix 4: Use Mobile Discord

Sometimes mobile Discord shows commands faster than desktop.

## 📱 **Mobile vs Desktop**

- **Mobile Discord**: Often shows commands faster
- **Desktop Discord**: May take longer to update
- **Web Discord**: Sometimes shows commands immediately

## 🔍 **Verification Commands**

Use these commands to verify everything is working:

### Owner Commands (You only)

```
/list_commands  # Shows all registered commands
/sync           # Manually sync commands
```

### Admin Commands (Server admins)

```
/performance    # Check bot performance
/cache          # Check cache status
/logs           # View recent logs
```

### User Commands (Everyone)

```
/help           # Get help
/time           # Check time
/auto_image_status  # Check auto-image status
```

## 🚨 **Emergency Commands**

If nothing else works, these commands should always be available:

### Prefix Commands (if slash commands fail)

```
!help
!time
```

### Direct Bot Mention

```
@Jakey help
@Jakey what commands do you have?
```

## 📞 **Still Not Working?**

If commands still don't appear after trying everything:

1. **Check bot logs** for sync errors
2. **Verify bot token** is correct
3. **Check Discord Developer Portal** - ensure bot has correct permissions
4. **Try in a new server** to isolate the issue
5. **Contact support** with:
   - Bot logs
   - `/list_commands` output
   - Server permissions screenshot

## ⏰ **Timeline Expectations**

- **Immediate**: Commands should work via `/list_commands`
- **1-2 minutes**: Commands should appear in Discord UI
- **5-10 minutes**: All Discord clients should show commands
- **1 hour**: Global propagation complete

---

**Remember**: The commands are working! It's just a matter of Discord's UI catching up.
