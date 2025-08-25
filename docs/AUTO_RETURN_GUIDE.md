# 🔄 Auto-Return System Guide

JakeyBot features an intelligent **auto-return system** that automatically manages tool usage, providing a seamless experience without manual intervention.

## 🎯 What is the Auto-Return System?

The auto-return system is JakeyBot's smart tool management feature that:

- **Automatically enables tools** when needed
- **Manages timeouts** intelligently based on tool type
- **Returns to Memory** after configurable timeouts
- **Provides smart suggestions** for optimization
- **Eliminates manual tool switching** for most use cases

## 🚀 Key Features

### **Automatic Tool Activation**

Tools are automatically enabled when JakeyBot detects they're needed:

```
User: "What's the price of Bitcoin?"
JakeyBot: 🔄 **Auto-enabled CryptoPrice** - Jakey needed this tool to help you!
         "Bitcoin is currently trading at $43,250 USD..."
```

### **Smart Timeout Management**

Different tools have optimized timeout durations:

| Tool Type | Default Timeout | Use Case |
|-----------|----------------|----------|
| **Memory** | Default | Personal conversations |
| **ExaSearch** | 3 minutes | Quick web searches |
| **CodeExecution** | 10 minutes | Complex calculations |
| **Image Generation** | 5 minutes | Image creation |
| **AudioTools** | 8 minutes | Audio processing |

### **Intelligent Suggestions**

Get personalized optimization tips:

```
/smart_suggestions
```

**Example suggestions:**

- "You've been using CodeExecution for 8 minutes. Consider extending with `/extend_timeout 5m`"
- "For image generation, try `/generate_image` directly - no tool switching needed!"
- "You're doing a lot of web searches. Consider using `/feature ExaSearch` for a longer session"

## 📋 Auto-Return Commands

### **Smart Suggestions**

Get personalized optimization advice:

```
/smart_suggestions
```

**What you get:**

- Workflow optimization tips
- Tool usage recommendations
- Performance insights
- Timeout management advice

### **Timeout Management**

#### **Check Remaining Time**

```
/timeout_status
```

**Example output:**

```
⏰ **Current Tool**: ExaSearch
⏱️ **Time Remaining**: 2 minutes 15 seconds
🔄 **Auto-return**: Will return to Memory in 2m 15s
```

#### **Extend Current Session**

```
/extend_timeout 5m    # Add 5 minutes
/extend_timeout 2h    # Add 2 hours
/extend_timeout 30m   # Add 30 minutes
```

**Supported time formats:**

- **Minutes**: `5m`, `15m`, `30m`
- **Hours**: `1h`, `2h`, `12h`
- **Days**: `1d`, `2d`, `1w`

#### **Return to Default Immediately**

```
/return_to_default
```

Forces immediate return to Memory tool.

### **System Status**

View auto-return system overview:

```
/auto_return_status
```

**Example output:**

```
🔄 **Auto-Return System Status**

✅ **System**: Active
🧠 **Default Tool**: Memory
⏰ **Current Tool**: ExaSearch
⏱️ **Time Remaining**: 1m 30s
📊 **Auto-enables**: 15 tools available
🎯 **Smart Suggestions**: Enabled

**Recent Activity:**
- Auto-enabled ExaSearch (2 minutes ago)
- Auto-enabled CryptoPrice (5 minutes ago)
- Returned to Memory (8 minutes ago)
```

## 🎯 How It Works

### **1. Automatic Detection**

JakeyBot analyzes your request and determines which tool is needed:

```
User: "Search for the latest AI news"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Performs web search and provides results]
```

### **2. Smart Timeout**

The system starts a countdown based on the tool type:

```
⏰ **ExaSearch Active** - Auto-returns to Memory in 3 minutes
```

### **3. Intelligent Return**

After the timeout, the tool automatically returns to Memory:

```
🔄 **Returned to Memory** - Back to personalized conversations!
```

### **4. Smart Suggestions**

The system learns from your usage patterns and provides optimization tips:

```
💡 **Smart Suggestion**: You're doing a lot of web searches. 
Consider using `/feature ExaSearch` for a longer session!
```

## 🔧 Configuration

### **Environment Variables**

Configure auto-return behavior in your `dev.env`:

```bash
# Default tool (usually Memory)
DEFAULT_TOOL=Memory

# Auto-return timeouts (in seconds)
AUTO_RETURN_TIMEOUT_EXASEARCH=180    # 3 minutes
AUTO_RETURN_TIMEOUT_CODEEXECUTION=600 # 10 minutes
AUTO_RETURN_TIMEOUT_IMAGEGEN=300     # 5 minutes
AUTO_RETURN_TIMEOUT_AUDIOTOOLS=480   # 8 minutes
```

### **Database Settings**

Auto-return settings are stored in the database:

```javascript
// Example database entry
{
  "user_id": "123456789",
  "guild_id": "987654321",
  "default_tool": "Memory",
  "auto_return_enabled": true,
  "timeout_settings": {
    "ExaSearch": 180,
    "CodeExecution": 600,
    "ImageGen": 300
  }
}
```

## 💡 Best Practices

### **For Users**

1. **Let it auto-enable**: Don't manually enable tools unless needed
2. **Use smart suggestions**: Get optimization tips regularly
3. **Extend timeouts**: Use `/extend_timeout` for longer sessions
4. **Monitor time**: Check `/timeout_status` to plan your work
5. **Plan workflows**: Since only one tool works at a time, plan your sequence

### **For Administrators**

1. **Configure timeouts**: Set appropriate timeout values for your use case
2. **Monitor usage**: Use management scripts to track tool usage
3. **Optimize defaults**: Set the most common tool as default
4. **Test thoroughly**: Verify auto-return behavior in your environment

## 🚨 Troubleshooting

### **Common Issues**

#### **Tool Not Auto-Enabling**

**Problem**: Tool doesn't automatically enable when needed

**Solutions**:

1. Check if the tool requires an API key
2. Verify the tool is properly configured
3. Check bot permissions and database connection

#### **Timeout Too Short**

**Problem**: Tools return to Memory too quickly

**Solutions**:

1. Use `/extend_timeout` to add more time
2. Configure longer timeouts in environment variables
3. Use `/feature <tool>` for manual control

#### **Smart Suggestions Not Working**

**Problem**: `/smart_suggestions` doesn't provide helpful tips

**Solutions**:

1. Ensure database connection is working
2. Check that usage tracking is enabled
3. Verify the command is properly registered

### **Error Messages**

#### **"Auto-return system unavailable"**

The auto-return system is disabled or not properly configured.

**Fix**: Check database connection and configuration.

#### **"Tool auto-enable failed"**

A tool failed to automatically enable.

**Fix**: Check tool configuration and API keys.

#### **"Timeout extension failed"**

Failed to extend the current tool session.

**Fix**: Check if the tool is still active and try again.

## 📊 Monitoring and Analytics

### **Usage Statistics**

Monitor auto-return system usage:

```bash
# Check system status
python scripts/manage_tools.py

# View auto-return statistics
python scripts/auto_return_stats.py
```

### **Performance Metrics**

Track key metrics:

- **Auto-enable success rate**: Percentage of successful auto-enables
- **Timeout adherence**: How often tools return on schedule
- **User satisfaction**: Based on smart suggestion usage
- **Tool distribution**: Which tools are most commonly auto-enabled

## 🔮 Future Enhancements

### **Planned Features**

- **Multi-tool support**: Use multiple tools simultaneously
- **Predictive auto-enable**: Anticipate tool needs based on conversation
- **Advanced analytics**: Detailed usage insights and optimization
- **Custom timeouts**: User-specific timeout preferences
- **Tool chaining**: Sequential tool execution with auto-return

### **Technical Improvements**

- **Better error handling**: Graceful fallbacks for tool failures
- **Performance optimization**: Faster tool switching
- **Intelligent caching**: Cache results to reduce API calls
- **Advanced suggestions**: AI-powered optimization recommendations

## 📚 Related Documentation

- **[TOOLS.md](./TOOLS.md)** - Complete tool documentation
- **[CONFIG.md](./CONFIG.md)** - Configuration guide
- **[FAQ.md](./FAQ.md)** - Common questions and answers
- **[MEMORY_QUICKSTART.md](./MEMORY_QUICKSTART.md)** - Memory tool guide

## 🆘 Getting Help

### **For Users**

1. **Check this guide** for detailed information
2. **Use `/smart_suggestions`** for optimization tips
3. **Try `/auto_return_status`** for system overview
4. **Ask server administrators** for configuration issues

### **For Administrators**

1. **Review configuration** in `dev.env`
2. **Check database connection** for persistence
3. **Monitor logs** for auto-return activity
4. **Test thoroughly** in your environment

---

**🔄 The auto-return system makes JakeyBot more intelligent and user-friendly by automatically managing tools for you!**
