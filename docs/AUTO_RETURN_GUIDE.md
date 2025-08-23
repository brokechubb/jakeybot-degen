# 🕐 Auto-Return Tool Manager Guide

JakeyBot now features an **automatic tool switching system** that intelligently manages tool usage and automatically returns users to their default tool (Memory) after a configurable timeout.

## 🎯 **What It Does**

### **Automatic Tool Management**
- **Smart Switching**: Automatically switches to requested tools
- **Timeout-Based Return**: Returns to default tool after configurable timeouts
- **User Experience**: No more forgotten tool switches
- **Personalization**: Always returns to Memory tool for personalization

### **How It Works**
1. **User switches tool** using `/feature <tool_name>`
2. **AutoReturnManager activates** and starts a countdown timer
3. **Timer runs** for the tool-specific timeout period
4. **Automatic return** to default tool (Memory) when timeout expires
5. **User continues** with personalized chat experience

## 🚀 **New Commands**

### **`/timeout_status`**
Check remaining time before auto-return to default tool.

**Example:**
```
User: /timeout_status
Bot: ⏰ Current Tool: ImageGen
     🕐 Time Remaining: 4m 23s
     🧠 Will Return To: Memory
```

### **`/extend_timeout <time>`**
Extend the current tool timeout by additional time.

**Examples:**
```
User: /extend_timeout 10m
Bot: ⏰ Timeout Extended!
     🛠️ Current Tool: ImageGen
     🕐 New Time Remaining: 14m 23s
     🧠 Will Return To: Memory

User: /extend_timeout 2h
Bot: ⏰ Timeout Extended!
     🛠️ Current Tool: ImageGen
     🕐 New Time Remaining: 2h 4m 23s
     🧠 Will Return To: Memory
```

### **`/return_to_default`**
Immediately return to the default tool.

**Example:**
```
User: /return_to_default
Bot: 🧠 Returned to Default Tool!
     ✅ Now using: Memory
     ⏰ Auto-return timer cancelled
```

### **`/auto_return_status`**
Check the status of the entire auto-return system.

**Example:**
```
User: /auto_return_status
Bot: 🧠 Auto-Return System Status

     ✅ Default Tool: Memory
     ⏰ Active Timers: 1
     🔄 Active Switches: 1

     Tool Timeouts:
     • AudioTools: 5m
     • CodeExecution: 10m
     • CryptoPrice: 3m
     • CurrencyConverter: 3m
     • ExaSearch: 3m
     • GitHub: 4m
     • IdeationTools: 5m
     • ImageGen: 5m
     • YouTube: 4m
     • Default: 5m
```

## ⚙️ **Configuration**

### **Environment Variables**
Add these to your `dev.env` file to customize timeouts:

```bash
# Tool-specific timeouts (in seconds)
TOOL_TIMEOUT_IMAGEGEN=300        # 5 minutes
TOOL_TIMEOUT_EXASEARCH=180       # 3 minutes
TOOL_TIMEOUT_GITHUB=240          # 4 minutes
TOOL_TIMEOUT_CODEEXECUTION=600   # 10 minutes
TOOL_TIMEOUT_AUDIOTOOLS=300      # 5 minutes
TOOL_TIMEOUT_CRYPTOPRICE=180     # 3 minutes
TOOL_TIMEOUT_CURRENCYCONVERTER=180 # 3 minutes
TOOL_TIMEOUT_YOUTUBE=240         # 4 minutes
TOOL_TIMEOUT_IDEATIONTOOLS=300   # 5 minutes
TOOL_TIMEOUT_DEFAULT=300         # 5 minutes default
```

### **Default Timeouts**
- **ImageGen**: 5 minutes (image generation takes time)
- **ExaSearch**: 3 minutes (quick web searches)
- **GitHub**: 4 minutes (repository operations)
- **CodeExecution**: 10 minutes (coding sessions)
- **AudioTools**: 5 minutes (audio processing)
- **CryptoPrice**: 3 minutes (quick price checks)
- **CurrencyConverter**: 3 minutes (quick conversions)
- **YouTube**: 4 minutes (video analysis)
- **IdeationTools**: 5 minutes (creative sessions)
- **Default**: 5 minutes (other tools)

## 🎮 **Usage Examples**

### **Scenario 1: Image Generation Session**
```
User: /feature ImageGen
Bot: ✅ Feature ImageGen enabled successfully!
     ⏰ Will automatically return to Memory in 5m

User: Generate a cat playing with yarn
Bot: [Generates image]

User: Make it more colorful
Bot: [Edits image]

User: /timeout_status
Bot: ⏰ Current Tool: ImageGen
     🕐 Time Remaining: 3m 45s
     🧠 Will Return To: Memory

User: /extend_timeout 10m
Bot: ⏰ Timeout Extended!
     🛠️ Current Tool: ImageGen
     🕐 New Time Remaining: 13m 45s
     🧠 Will Return To: Memory

[After 13m 45s, bot automatically switches back to Memory]
```

### **Scenario 2: Web Search Session**
```
User: /feature ExaSearch
Bot: ✅ Feature ExaSearch enabled successfully!
     ⏰ Will automatically return to Memory in 3m

User: What's the latest news about AI?
Bot: [Searches web and provides results]

User: Search for cryptocurrency prices
Bot: [Searches for crypto information]

[After 3 minutes, bot automatically switches back to Memory]

User: What do you know about me?
Bot: [Uses Memory tool to recall personal information]
```

### **Scenario 3: Immediate Return**
```
User: /feature GitHub
Bot: ✅ Feature GitHub enabled successfully!
     ⏰ Will automatically return to Memory in 4m

User: /return_to_default
Bot: 🧠 Returned to Default Tool!
     ✅ Now using: Memory
     ⏰ Auto-return timer cancelled

User: What's my favorite color?
Bot: [Uses Memory tool to recall personal preference]
```

## 🔧 **Technical Details**

### **How Timeouts Work**
1. **Timer Creation**: When a tool is switched, a countdown timer is created
2. **Background Processing**: Timer runs asynchronously in the background
3. **Automatic Return**: When timer expires, bot automatically switches back to default
4. **Database Update**: Tool configuration is updated in the database
5. **Timer Cleanup**: Timer and switch information are cleaned up

### **Timer Management**
- **Individual Timers**: Each user/guild has their own timer
- **Timer Cancellation**: Timers can be cancelled or extended
- **Cleanup**: All timers are cleaned up when bot shuts down
- **Error Handling**: Graceful fallback if auto-return fails

### **Database Integration**
- **Tool Configuration**: Integrates with existing tool configuration system
- **User Isolation**: Each user's tool preferences are maintained
- **Guild Support**: Works with both individual users and guilds
- **Shared History**: Compatible with shared chat history setting

## 🎯 **Best Practices**

### **For Users**
1. **Use `/feature` normally** - Auto-return happens automatically
2. **Check `/timeout_status`** - Monitor remaining time
3. **Extend timeouts** - Use `/extend_timeout` for longer sessions
4. **Return early** - Use `/return_to_default` when done
5. **Plan your workflow** - Know which tool you need before starting

### **For Administrators**
1. **Configure timeouts** - Set appropriate timeouts for your server
2. **Monitor usage** - Use `/auto_return_status` to check system health
3. **Customize defaults** - Adjust timeouts based on user needs
4. **Test functionality** - Use test script to verify system works

## 🚨 **Troubleshooting**

### **Common Issues**

**Auto-return not working:**
1. Check if AutoReturnManager is initialized
2. Verify database connection
3. Check bot logs for errors
4. Ensure environment variables are set

**Timer not accurate:**
1. Check system time synchronization
2. Verify timeout configuration
3. Monitor for timer conflicts
4. Check for multiple bot instances

**Tool not switching back:**
1. Use `/return_to_default` to force return
2. Check database tool configuration
3. Verify AutoReturnManager status
4. Restart bot if necessary

### **Getting Help**
1. **Check system status**: `/auto_return_status`
2. **Monitor timers**: `/timeout_status`
3. **Review logs**: Check bot console output
4. **Test functionality**: Run `python scripts/test_auto_return.py`

## 🎉 **Benefits**

### **User Experience**
- ✅ **No forgotten tools** - Always returns to Memory
- ✅ **Seamless workflow** - Automatic tool management
- ✅ **Personalization** - Memory tool always available
- ✅ **Flexible timeouts** - Extend or return early

### **Administration**
- ✅ **Configurable timeouts** - Per-tool customization
- ✅ **System monitoring** - Status and health checks
- ✅ **Error handling** - Graceful fallbacks
- ✅ **Resource management** - Automatic cleanup

### **Performance**
- ✅ **Efficient timers** - Async background processing
- ✅ **Memory management** - Automatic cleanup
- ✅ **Database integration** - Seamless operation
- ✅ **Scalable design** - Handles multiple users

---

**🚀 The AutoReturnManager makes JakeyBot truly intelligent by automatically managing tool usage and ensuring users always return to their personalized Memory experience!**
