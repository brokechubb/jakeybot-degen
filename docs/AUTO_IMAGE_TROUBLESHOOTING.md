# 🎨 Auto Image Generation Troubleshooting Guide

This guide helps you diagnose and fix issues with JakeyBot's auto image generation system.

## 🔍 Quick Diagnosis

### Check System Status

Use the `/auto_image_debug` command to get a comprehensive status report:

```
/auto_image_debug
```

This will show you:

- ✅/❌ Settings Loaded
- ✅/❌ Gemini API Configured  
- ✅/❌ Database Connection
- Current guild settings
- Total guilds loaded

### Check Current Status

Use the `/auto_image_status` command to see the current state:

```
/auto_image_status
```

## 🚨 Common Issues & Solutions

### Issue 1: "Settings Loaded: ❌"

**Problem**: Auto-image settings haven't been loaded from the database yet.

**Solutions**:

1. **Wait for initialization**: The bot needs time to load settings on startup
2. **Check database connection**: Ensure MongoDB is running and accessible
3. **Restart the bot**: If settings don't load after 30 seconds, restart the bot

**Debug Steps**:

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Check bot logs for database errors
tail -f logs/jakeybot.log | grep -i "database\|auto.*image"
```

### Issue 2: "Gemini API: ❌"

**Problem**: The Gemini API key is not configured or invalid.

**Solutions**:

1. **Set API key**: Add `GEMINI_API_KEY=your_key_here` to `dev.env`
2. **Verify key**: Ensure the API key is valid and has image generation permissions
3. **Restart bot**: Restart the bot after adding the API key

**Debug Steps**:

```bash
# Check if API key is set
grep GEMINI_API_KEY dev.env

# Test API key manually
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     https://generativelanguage.googleapis.com/v1beta/models
```

### Issue 3: "Auto-Image Enabled: ❌"

**Problem**: Auto-image generation is disabled for your server.

**Solutions**:

1. **Enable auto-image**: Use `/auto_image true` (requires Manage Channels permission)
2. **Check permissions**: Ensure you have "Manage Channels" permission
3. **Contact admin**: Ask a server admin to enable the feature

**Debug Steps**:

```bash
# Check your permissions
# Look for "Manage Channels" in your role permissions

# Check current setting
/auto_image_status
```

### Issue 4: Messages Not Detected

**Problem**: The bot doesn't respond to image requests.

**Solutions**:

1. **Use proper format**: Mention the bot or use prefix commands
   - `@Jakey draw me a cat`
   - `!jakey create an image of a dog`
   - `Jakey generate a picture of a sunset`
2. **Use image keywords**: Include words like "draw", "create", "generate", "image", "picture"
3. **Wait for loading**: Ensure settings are loaded (check `/auto_image_debug`)

**Debug Steps**:

```bash
# Test with these exact phrases:
@Jakey draw me a cat
@Jakey create an image of a dog
@Jakey generate a picture of a sunset
```

### Issue 5: Auto-Generation Fails

**Problem**: Auto-generation starts but fails to create images.

**Solutions**:

1. **Check Gemini model**: Ensure the model supports image generation
2. **Verify prompt**: Make sure the prompt is substantial (>3 characters)
3. **Check safety filters**: Some prompts may be blocked by content filters
4. **Use manual commands**: Try `/generate_image` or `/generate_pollinations` instead

**Debug Steps**:

```bash
# Check bot logs for generation errors
tail -f logs/jakeybot.log | grep -i "auto.*generation\|gemini"

# Test with simple prompts
@Jakey draw a simple circle
@Jakey create a basic square
```

## 🛠️ Advanced Troubleshooting

### Database Issues

If auto-image settings aren't persisting:

```python
# Check database connection
from core.services.database_manager import DatabaseManager
db = DatabaseManager()
await db.test_connection()

# Check auto-image settings in database
guild_doc = await db._collection.find_one({"guild_id": "YOUR_GUILD_ID"})
print(guild_doc.get("auto_image_enabled", "Not found"))
```

### API Configuration Issues

If Gemini API isn't working:

```python
# Test Gemini configuration
import google.generativeai as genai
from os import environ

api_key = environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
    print("Gemini configured successfully")
else:
    print("No Gemini API key found")
```

### Performance Issues

If auto-generation is slow:

1. **Check network**: Ensure stable internet connection
2. **Monitor resources**: Check CPU and memory usage
3. **Use caching**: The system caches results for better performance
4. **Consider alternatives**: Use `/generate_pollinations` for faster generation

## 📋 Testing Checklist

Before reporting an issue, verify these items:

- [ ] Bot is online and responding to commands
- [ ] `/auto_image_debug` shows all systems ✅
- [ ] `/auto_image_status` shows enabled for your server
- [ ] You have "Manage Channels" permission
- [ ] `GEMINI_API_KEY` is set in `dev.env`
- [ ] MongoDB is running and accessible
- [ ] You're using proper mention/prefix format
- [ ] Your prompt contains image-related keywords
- [ ] Prompt is longer than 3 characters

## 🔧 Manual Override

If auto-generation isn't working, use these manual commands:

```bash
# Generate image with Gemini
/generate_image your prompt here

# Generate image with Pollinations.AI
/generate_pollinations your prompt here

# Edit existing image
/edit_image your edit prompt here
```

## 📞 Getting Help

If you're still having issues:

1. **Check logs**: Look for error messages in the bot logs
2. **Use debug command**: Run `/auto_image_debug` and share the output
3. **Test manually**: Try the manual image generation commands
4. **Contact support**: Open an issue on GitHub with:
   - Debug command output
   - Error messages from logs
   - Steps to reproduce the issue
   - Your bot configuration (without API keys)

## 🎯 Quick Fixes

### Most Common Solutions

1. **Enable auto-image**: `/auto_image true`
2. **Set API key**: Add `GEMINI_API_KEY=your_key` to `dev.env`
3. **Restart bot**: After configuration changes
4. **Use proper format**: `@Jakey draw me a cat`
5. **Check permissions**: Ensure "Manage Channels" permission

### Emergency Commands

```bash
# Force reload settings
/auto_image_debug

# Check current status  
/auto_image_status

# Manual generation
/generate_image test image
/generate_pollinations test image
```

---

**Remember**: Auto-image generation is a convenience feature. Manual commands (`/generate_image`, `/generate_pollinations`) always work and provide more control.
