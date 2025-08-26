# 🎵 JakeyBot Music Guide

Welcome to JakeyBot's music system! This guide will help you set up and use the LavaLink v4 music features for voice channels.

## 🚀 **Quick Start**

### **1. Enable Music Features**

Add these settings to your `dev.env` file:

```bash
# Enable voice features
ENABLE_VOICE_FEATURES=true
LAVALINK_V4_ENABLED=true

# LavaLink v4 server configuration
ENV_LAVALINK_URI=http://127.0.0.1:2333
ENV_LAVALINK_PASS=youshallnotpass
ENV_LAVALINK_IDENTIFIER=main
```

### **2. Choose a LavaLink Server**

#### **Option A: Free Public Servers (Recommended for Testing)**

Use servers from [LavaLink Servers](https://lavalink.darrennathanael.com/NoSSL/lavalink-without-ssl/):

```bash
# Example configuration for a public server
ENV_LAVALINK_URI=http://lavalink.oops.wtf:2000
ENV_LAVALINK_PASS=www.freelavalink.ga
ENV_LAVALINK_IDENTIFIER=main
```

#### **Option B: Host Your Own Server**

1. **Install OpenJDK 17+**
2. **Download LavaLink v4**
3. **Configure and run the server**

### **3. Install Dependencies**

```bash
pip install wavelink[voice]>=3.0.0
```

### **4. Restart JakeyBot**

```bash
python main.py
```

## 🎮 **Music Commands**

### **Basic Playback**

| Command | Description | Example |
|---------|-------------|---------|
| `/play <query>` | Play music from YouTube, Spotify, or other sources | `/play despacito` |
| `/pause` | Pause the current music | `/pause` |
| `/resume` | Resume the paused music | `/resume` |
| `/stop` | Stop playing and clear the queue | `/stop` |
| `/skip` | Skip the current track (vote-based) | `/skip` |

### **Queue Management**

| Command | Description | Example |
|---------|-------------|---------|
| `/queue` | Show the current music queue | `/queue` |
| `/nowplaying` | Show information about the currently playing track | `/nowplaying` |

### **Volume Control**

| Command | Description | Example |
|---------|-------------|---------|
| `/volume <level>` | Set the music volume (0-100) | `/volume 75` |

### **Voice Channel**

| Command | Description | Example |
|---------|-------------|---------|
| `/disconnect` | Disconnect from the voice channel | `/disconnect` |

## 🎯 **How to Use**

### **Playing Music**

1. **Join a voice channel** in your Discord server
2. **Use `/play`** with a song name, artist, or URL:

   ```
   /play despacito
   /play https://www.youtube.com/watch?v=dQw4w9WgXcQ
   /play spotify:track:4iV5W9uYEdYUVa79Axb7Rh
   ```

3. **JakeyBot will join** your voice channel and start playing!

### **Managing the Queue**

- **Add more songs** while one is playing - they'll be added to the queue
- **View the queue** with `/queue` to see upcoming tracks
- **Skip tracks** with `/skip` (requires votes from other users)

### **Volume Control**

- **Set volume** with `/volume 75` (0-100)
- **Default volume** is 50%
- **Maximum volume** is 100%

## 🔧 **Configuration Options**

### **Environment Variables**

```bash
# Voice features
ENABLE_VOICE_FEATURES=true
LAVALINK_V4_ENABLED=true

# LavaLink server
ENV_LAVALINK_URI=http://127.0.0.1:2333
ENV_LAVALINK_PASS=youshallnotpass
ENV_LAVALINK_IDENTIFIER=main

# Voice settings
VOICE_TIMEOUT=300          # Auto-disconnect after 5 minutes of inactivity
MAX_QUEUE_SIZE=50          # Maximum tracks in queue
DEFAULT_VOLUME=50          # Default volume level
MAX_VOLUME=100             # Maximum allowed volume

# LavaLink settings
LAVALINK_V4_RETRY_ATTEMPTS=3
LAVALINK_V4_RETRY_DELAY=5
```

### **Bot Permissions**

Ensure JakeyBot has these permissions in your Discord server:

- ✅ **Connect** - Join voice channels
- ✅ **Speak** - Play audio in voice channels
- ✅ **Use Voice Activity** - Access voice features
- ✅ **Send Messages** - Respond to commands
- ✅ **Use Slash Commands** - Execute music commands

## 🎵 **Supported Sources**

JakeyBot supports music from various sources:

### **YouTube**

- Direct YouTube URLs
- YouTube search queries
- YouTube playlists

### **Spotify**

- Spotify track URLs
- Spotify album URLs
- Spotify playlist URLs

### **Other Sources**

- SoundCloud
- Bandcamp
- Direct audio file URLs
- And more (depends on LavaLink server)

## 🎮 **Advanced Features**

### **Vote-based Skipping**

- **3 votes required** to skip a track
- **Votes reset** after each skip
- **Democratic control** of music playback

### **Queue Management**

- **Automatic queue** - songs are added when one is already playing
- **Queue display** - see upcoming tracks with `/queue`
- **Queue limits** - configurable maximum queue size

### **Auto-disconnect**

- **Inactivity timeout** - bot leaves after 5 minutes of no music
- **Configurable timeout** - adjust with `VOICE_TIMEOUT` setting
- **Smart reconnection** - joins automatically when you use `/play`

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"Voice features are disabled"**

- Check `ENABLE_VOICE_FEATURES=true` in dev.env
- Check `LAVALINK_V4_ENABLED=true` in dev.env

#### **"Failed to connect to LavaLink node"**

- Verify LavaLink server is running
- Check `ENV_LAVALINK_URI` and `ENV_LAVALINK_PASS`
- Try a different LavaLink server

#### **"No tracks found"**

- Try a different search query
- Check if the LavaLink server supports the source
- Verify the URL is valid

#### **"Cannot join voice channel"**

- Check bot permissions (Connect, Speak)
- Ensure you're in a voice channel
- Verify the bot isn't already in another voice channel

#### **"Music not playing"**

- Check bot volume settings
- Verify your Discord client volume
- Try reconnecting with `/disconnect` then `/play`

### **Debugging Steps**

1. **Check bot logs** for LavaLink connection errors
2. **Verify environment variables** are set correctly
3. **Test with a public LavaLink server** first
4. **Check Discord permissions** in server settings
5. **Restart the bot** after configuration changes

## 📋 **Best Practices**

### **For Users**

- **Use descriptive queries** - "artist - song name" works best
- **Be patient** - some tracks take time to load
- **Respect the queue** - don't spam skip votes
- **Check volume** - start with `/volume 50` and adjust

### **For Server Admins**

- **Monitor usage** - music features can be resource-intensive
- **Set appropriate timeouts** - prevent bots from staying connected indefinitely
- **Use reliable LavaLink servers** - public servers may have downtime
- **Consider hosting your own** - for production use

## ⚠️ **Important Notes**

### **Terms of Service**

- **Do not use in production** unless you're serving your own content
- **Never verify your bot** with YouTube playback features
- **Respect copyright** and licensing requirements
- **Use responsibly** - don't abuse public LavaLink servers

### **Performance Considerations**

- **Voice features** require additional resources
- **LavaLink servers** may have rate limits
- **Queue management** uses memory for each guild
- **Network bandwidth** is used for audio streaming

## 🆘 **Getting Help**

### **Support Resources**

- **Configuration issues**: Check `docs/CONFIG.md`
- **Bot permissions**: Review Discord server settings
- **LavaLink problems**: Check server status and configuration
- **General help**: Use `/help` command in Discord

### **Useful Commands**

```bash
# Check if music features are enabled
/help

# Test music functionality
/play despacito

# Check current status
/nowplaying

# View queue
/queue
```

---

**🎵 Happy listening! Remember to respect copyright and use music features responsibly.**
