# 🎮 JakeyBot Discord User Guide

Welcome to JakeyBot! This guide will help you get the most out of your interactions with this AI-powered Discord bot.

## 🚀 **Getting Started**

### **First Time Setup**

1. **Invite JakeyBot** to your Discord server
2. **Grant necessary permissions** (Send Messages, Read Message History, etc.)
3. **Start chatting!** JakeyBot will respond to your messages automatically

### **Basic Commands**

| Command | Description | Example |
|---------|-------------|---------|
| Mention Jakey | Ask JakeyBot a question | @JakeyBot What's the weather like? |
| `/time` | Displays the current time and DST status | `/time` |
| `/remind` | Set a reminder for yourself | `/remind time_in:1h message:Take a break` |
| `/sweep` | Clear conversation history | `/sweep` |
| `/model set` | Switch AI models | `/model set pollinations::openai` |
| `/feature <tool>` | Enable/disable tools | `/feature Memory` |
| `/jakey_engage` | Make Jakey actively engage in the current channel | `/jakey_engage` |
| `/jakey_disengage` | Stop Jakey's active engagement | `/jakey_disengage` |
| `/create_bet` | Create a new betting pool | `/create_bet title:Super Bowl options:Chiefs,49ers` |
| `/cancel_bet` | Cancel the current betting pool | `/cancel_bet` |
| `/trivia` | Start a trivia game | `/trivia` |
| `/cancel_trivia` | Cancel the current trivia game | `/cancel_trivia` |
| `/keno` | Generate random keno numbers | `/keno` |
| `/generate_image` | Generate AI images | `/generate_image a cute cat` |
| `/edit_image` | Edit images with AI | `/edit_image add a hat` |

### **Auto-Return System Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/smart_suggestions` | Get optimization tips | `/smart_suggestions` |
| `/extend_timeout` | Extend tool session time | `/extend_timeout 5m` |
| `/timeout_status` | Check remaining time | `/timeout_status` |
| `/return_to_default` | Return to Memory immediately | `/return_to_default` |
| `/auto_return_status` | View system status | `/auto_return_status` |

### **Help & Support Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Comprehensive help and quickstart guide | `/help` |
| `/quickstart` | Step-by-step getting started guide | `/quickstart` |
| `/memory_debug` | Debug memory system status | `/memory_debug` |
| `/memory_reindex` | Fix memory search issues | `/memory_reindex` |

## 🆘 **Help & Support System**

### **Getting Help with JakeyBot**

JakeyBot now includes comprehensive help commands to guide you through all features and capabilities:

#### **`/help` - Complete Help Guide**

- **Comprehensive overview** of all available features
- **AI model information** with API key requirements
- **Tool descriptions** and capabilities
- **Pro tips** and best practices
- **Troubleshooting** guide for common issues
- **Admin commands** for server administrators

#### **`/quickstart` - Getting Started Guide**

- **3-step process** to get up and running
- **Essential commands** to try first
- **Feature overview** of what Jakey can do
- **Actionable next steps** for new users

#### **Help Features**

- **API Key Requirements**: Clear information about what keys are needed
- **Command Examples**: Copy-paste ready command examples
- **Troubleshooting**: Solutions for common problems
- **Cross-References**: Links between related commands and features

### **When to Use Help Commands**

- **New Users**: Start with `/quickstart` for step-by-step guidance
- **Feature Discovery**: Use `/help` to explore all capabilities
- **Problem Solving**: Check troubleshooting section for solutions
- **Admin Tasks**: Find administrative commands and tools

## 🔄 **Auto-Return System** ⭐ **NEW FEATURE**

### **What is the Auto-Return System?**

JakeyBot features an intelligent **auto-return system** that automatically manages tool usage:

- **Automatic Tool Activation**: Tools are automatically enabled when needed
- **Smart Timeout Management**: Tools return to Memory after configurable timeouts
- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Seamless Experience**: No manual tool management required

### **🎯 How Auto Tool Switch Works**

**Just ask naturally** - JakeyBot automatically detects what tool you need:

```
User: "What's the price of Bitcoin?"
JakeyBot: 🔄 **Auto-enabled CryptoPrice** - Jakey needed this tool to help you!
         "💰 Current BTC: $43,250 USD"

User: "Search for the latest AI news"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Searches web and provides current information]

User: "Convert 100 USD to EUR"
JakeyBot: 🔄 **Auto-enabled CurrencyConverter** - Jakey needed this tool to help you!
         "💱 100 USD = 92.50 EUR"

User: "Calculate 15% of 250"
JakeyBot: 🔄 **Auto-enabled CodeExecution** - Jakey needed this tool to help you!
         "15% of 250 = 37.5"

User: "What's the weather like in Tokyo?"
JakeyBot: �� **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Searches for current Tokyo weather]
```

### **🚀 Key Benefits**

- **✅ No Manual Tool Switching** - Tools enable automatically when needed
- **✅ Smart Timeout Management** - Tools return to Memory after optimal timeouts
- **✅ Intelligent Suggestions** - Get optimization tips with `/smart_suggestions`
- **✅ Seamless Experience** - Focus on your questions, not tool management

### **How It Works**

1. **Automatic Detection**: JakeyBot analyzes your request and determines which tool is needed
2. **Smart Timeout**: The system starts a countdown based on the tool type
3. **Intelligent Return**: After the timeout, the tool automatically returns to Memory
4. **Smart Suggestions**: The system learns from your usage patterns and provides optimization tips

### **Auto-Return Commands**

#### **Smart Suggestions**

Get personalized optimization advice:

```
/smart_suggestions
```

**What you get:**

- Workflow optimization tips
- Tool usage recommendations
- Performance insights
- Timeout management advice

#### **Timeout Management**

**Check Remaining Time:**

```
/timeout_status
```

**Extend Current Session:**

```
/extend_timeout 5m    # Add 5 minutes
/extend_timeout 2h    # Add 2 hours
/extend_timeout 30m   # Add 30 minutes
```

**Return to Default Immediately:**

```
/return_to_default
```

#### **System Status**

View auto-return system overview:

```
/auto_return_status
```

### **Timeout Durations**

| Tool Type | Default Timeout | Use Case |
|-----------|----------------|----------|
| **Memory** | Default | Personal conversations |
| **ExaSearch** | 3 minutes | Quick web searches |
| **CodeExecution** | 10 minutes | Complex calculations |
| **Image Generation** | 5 minutes | Image creation |

## ⏰ **Personal Reminder System**

### **What is the Reminder System?**

JakeyBot now includes a **personal reminder system** that lets you set reminders for yourself using natural language! It's perfect for remembering important tasks, meetings, or just taking breaks.

### **How to Use Reminders**

**Basic Reminder Syntax:**

```
/remind time_in:<time> message:<what to remind you about>
```

**Examples:**

```
/remind time_in:1h message:Take a break from coding
/remind time_in:30m message:Check crypto prices
/remind time_in:tomorrow 10am message:Daily standup meeting
/remind time_in:2d message:Pay rent
```

### **Time Formats Supported**

**Simple Formats:**

- **Minutes**: `30m`, `15m`, `45m`
- **Hours**: `1h`, `2h`, `12h`
- **Days**: `1d`, `2d`, `1w`

**Natural Language:**

- `tomorrow 10am`
- `next week`
- `in 2 hours`
- `next Monday`

### **Reminder Features**

- ✅ **Automatic delivery** - Bot sends reminders when due
- ✅ **Personal reminders** - Only you can see your reminders
- ✅ **Natural language** - Understands human-like time expressions
- ✅ **Flexible commands** - Works with both `/remind` and `$remind`
- ✅ **Background processing** - Bot checks reminders every minute

### **Reminder Best Practices**

1. **Be specific**: "pay rent" vs "reminder"
2. **Use natural language**: "tomorrow 10am" vs "24h"
3. **Set reasonable times**: Avoid very short or very long reminders
4. **Clear messages**: Make sure the reminder message is clear

## 🕐 **Time & Date Commands**

### **Current Time Display**

Get the current time and timezone information:

**Command:** `/time` or `$time`

**What You Get:**

- Current date and time
- Timezone information (EDT, PST, etc.)
- Daylight Saving Time status
- Both slash and prefix command support

**Example Output:**

```
The current time is 2025-08-23 14:30:25 EDT-0400. 
Daylight Saving Time is currently active.
```

## 🧠 **Memory System - Your Personal AI Assistant**

### **What is Memory?**

JakeyBot can now **remember information about you** across conversations! It's like having a personal AI assistant that knows your preferences, interests, and important details.

### **How It Works**

**Automatic Memory:**

- Just **share information naturally** in conversation
- JakeyBot **automatically detects** and remembers it
- **No special commands needed** - it just works!

**Examples:**

```
You: "My name is Alex and I love playing guitar"
JakeyBot: "Nice to meet you, Alex! I'll remember that you love playing guitar."

Later...
You: "What do you know about me?"
JakeyBot: "Your name is Alex and you love playing guitar!"
```

### **What Gets Remembered**

**✅ Personal Information:**

- Names and nicknames
- Hobbies and interests
- Preferences (food, music, games)
- Skills and expertise
- Important dates
- Relationships and pets

**❌ Not Remembered:**

- Commands and instructions
- Temporary requests
- Non-personal information
- Sensitive data

### **Memory Management Commands**

- **`/remember <fact>`** - Manually store information
- **`/feature Memory`** - Enable the Memory tool
- **`/memory_debug`** - Check memory system status
- **`/memory_reindex`** - Fix search issues by reindexing

### **Memory Debugging**

**When to Use `/memory_debug`:**

- Check if memory is working properly
- Verify database connection status
- See memory system statistics
- Troubleshoot memory issues

**When to Use `/memory_reindex`:**

- Fix search problems
- Resolve missing information issues
- Improve search accuracy
- After database changes

## 🎨 **Image Generation & Editing**

### **Direct Image Generation**

JakeyBot can generate images from your descriptions using AI! **No tool switching required**:

**Commands:**

- `/generate_image <prompt>` - Generate AI images
- `/edit_image <prompt>` - Edit images with AI

**Examples:**

```
/generate_image a cute cat playing with a ball of yarn
/generate_image futuristic city skyline at sunset
/edit_image add a hat to this person
/edit_image make this image more colorful
```

### **Features**

- **Direct Commands**: No need to enable tools
- **AI-Powered**: Uses advanced AI models for creation
- **Multiple Models**: Support for various image generation models
- **Advanced Editing**: Modify existing images with AI

## 🎮 **Interactive Features**

### **Engagement System**

JakeyBot can actively participate in your channels:

**Commands:**

- `/jakey_engage` - Make Jakey actively engage in the current channel
- `/jakey_disengage` - Stop Jakey's active engagement

**Features:**

- **Active Participation**: Jakey can actively engage in channels
- **Persistent Settings**: Engagement settings survive bot restarts
- **Smart Interjections**: Context-aware participation
- **Configurable Behavior**: Adjust engagement frequency and style

### **Gambling Games**

Interactive gambling and gaming features:

**Commands:**

- `/create_bet <title> <options>` - Create a new betting pool
- `/cancel_bet` - Cancel the current betting pool
- `/trivia` - Start a trivia game
- `/cancel_trivia` - Cancel the current trivia game
- `/keno` - Generate random keno numbers

**Features:**

- **Betting Pools**: Create community betting pools
- **Trivia Games**: Interactive trivia with AI-generated questions
- **Keno Numbers**: Generate random keno numbers
- **Leaderboards**: Track scores and winners

**Examples:**

```
/create_bet "Who will win the game?" "Team A,Team B,Team C"
/trivia
/keno
```

## 🔍 **Web Search & Information**

### **Real-Time Information**

JakeyBot can search the web for current information:

**Examples:**

```
You: "What's the latest news about AI?"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Searches web and provides current information]

You: "What's the weather in Tokyo right now?"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Gets real-time weather data]
```

**Examples:**

```

```

## 💰 **Crypto & Financial Tools**

### **Live Crypto Prices**

Get real-time cryptocurrency prices:

**Examples:**

```
You: "What's the current price of Bitcoin?"
JakeyBot: 🔄 **Auto-enabled CryptoPrice** - Jakey needed this tool to help you!
         "💰 Current BTC: $43,250 USD"

You: "How much is 100 SOL worth in USD?"
JakeyBot: 🔄 **Auto-enabled CryptoPrice** - Jakey needed this tool to help you!
         [Converts and shows current value]
```

### **Currency Conversion**

Convert between 170+ world currencies:

**Examples:**

```
You: "Convert 1000 EUR to USD"
JakeyBot: 🔄 **Auto-enabled CurrencyConverter** - Jakey needed this tool to help you!
         "💱 1,000 EUR = 1,085 USD"

You: "What's 50,000 JPY in GBP?"
JakeyBot: 🔄 **Auto-enabled CurrencyConverter** - Jakey needed this tool to help you!
         [Shows conversion with current rates]
```

## 🎵 **Audio Tools**

### **Voice Cloning & Audio Editing**

JakeyBot can help with audio manipulation:

**Examples:**

```

```

## 💻 **Code Execution**

### **Python Code Running**

JakeyBot can execute Python code for you:

**Examples:**

```
You: "Calculate the factorial of 10"
JakeyBot: 🔄 **Auto-enabled CodeExecution** - Jakey needed this tool to help you!
         [Runs Python code and returns result]

You: "Generate a random password"
JakeyBot: 🔄 **Auto-enabled CodeExecution** - Jakey needed this tool to help you!
         [Executes code to create password]
```

## 🎯 **Pro Tips & Best Practices**

### **Getting Better Responses**

1. **Be specific** - "Generate a red sports car" vs "make a car"
2. **Provide context** - "I need this for a presentation about AI"
3. **Use natural language** - Talk to JakeyBot like a person

### **Auto-Return System**

- **Let tools auto-enable**: Most tools are automatically enabled when needed
- **Use smart suggestions**: Get optimization tips with `/smart_suggestions`
- **Monitor timeouts**: Check `/timeout_status` to plan your work
- **Extend sessions**: Use `/extend_timeout` for longer sessions

### **Tool Usage**

- **One tool at a time** - Only one tool can be active per conversation
- **Auto-enablement** - Tools are automatically enabled when needed
- **Smart management** - Use auto-return system for seamless experience

### **Memory Optimization**

- **Share information naturally** - Don't force it
- **Be consistent** - Use the same terms for things
- **Update preferences** - Tell JakeyBot when things change

### **Reminder Best Practices**

- **Use natural language**: "tomorrow 10am" vs "24h"
- **Be specific**: "pay rent" vs "reminder"
- **Set reasonable times**: Avoid very short or very long reminders

### **Interactive Features**

- **Use `/jakey_engage`** to invite Jakey into the conversation
- **Try `/create_bet` and `/trivia`** for interactive games
- **Generate images directly** with `/generate_image`
- **Use smart suggestions** for optimization advice

## 🚨 **Troubleshooting**

### **Common Issues**

**JakeyBot not responding:**

- Check if the bot is online
- Verify bot has proper permissions
- Try mentioning Jakey directly

**Tool not working:**

- Tools are automatically enabled when needed
- Check if the tool is available in your server
- Contact server administrators

**Memory not working:**

- Ensure Memory tool is enabled: `/feature Memory`
- Try sharing some information first
- Check if the bot has database access
- Use `/memory_debug` to check system status

**Reminders not working:**

- Check database connection with `/memory_debug`
- Verify the reminder was set correctly
- Ensure the bot has permission to send messages

**Auto-return system issues:**

- Check `/auto_return_status` for system overview
- Use `/smart_suggestions` for optimization tips
- Verify database connection is working

### **Getting Help**

1. **Check bot status** - Look for the green "Online" indicator
2. **Verify permissions** - Bot needs Send Messages, Read Message History
3. **Ask server admins** - They can check bot configuration
4. **Use `/feature`** - See what tools are available
5. **Debug memory** - Use `/memory_debug` for memory issues
6. **Get smart suggestions** - Use `/smart_suggestions` for optimization

## 🎭 **Understanding JakeyBot's Personality**

### **What to Expect**

JakeyBot has a **unique, unfiltered personality**:

- **Direct and honest** - No sugar-coating
- **Crypto and gambling expert** - Knows about trading, betting, casinos
- **Internet culture savvy** - Uses modern slang and emojis
- **Slightly rude** - But in a fun, entertaining way

### **Personality Examples**

```
You: "What do you think about this investment?"
JakeyBot: "bro that's a terrible idea fr 💀 but hey, your money your problem"

You: "Can you help me with my homework?"
JakeyBot: "sure, but don't blame me if you fail the test 😂"
```

## 🔒 **Privacy & Data**

### **What JakeyBot Remembers**

- **Conversation context** - For better responses
- **Personal preferences** - To personalize your experience
- **Tool usage** - To improve functionality
- **Personal reminders** - Only visible to you

### **What JakeyBot Doesn't Store**

- **Sensitive personal information**
- **Passwords or credentials**
- **Private messages** (unless you explicitly share them)

### **Data Control**

- **Clear conversations** - Use `/sweep` to clear history
- **Memory management** - Information is stored per user/server
- **Privacy settings** - Contact server admins for privacy concerns

## 🎉 **Advanced Features**

### **AI Model Selection**

Different AI models have different strengths:

- **Gemini** - Great for general chat and creativity
- **GPT-4** - Excellent for analysis and reasoning
- **Claude** - Strong for writing and explanation
- **Pollinations.AI** - Uncensored models for unfiltered responses
- **Specialized models** - For specific tasks

### **Model Switching**

Use `/model set` to switch between different AI models:

```
/model set gemini::gemini-2.5-flash
/model set openai::gpt-5
/model set pollinations::evil
```

### **Custom Tool Combinations**

While only one tool can be active at a time, you can:

1. **Use Memory tool** for personalization
2. **Use image generation commands** for image creation
3. **Use ExaSearch** for web research
4. **Return to Memory** to continue personalized conversations

## 📚 **Additional Resources**

### **Server-Specific Features**

Your server may have additional features enabled:

- **Custom commands** - Ask server admins
- **Special tools** - Check with `/feature`
- **Server-specific memory** - Some servers share context

### **Getting More Help**

- **Server admins** - For technical issues
- **Bot documentation** - For detailed information
- **Community support** - Join JakeyBot community servers

---

## 🎯 **Quick Reference**

### **Essential Commands**

- Mention Jakey with your question
- `/feature <tool>` - Enable tools
- `/sweep` - Clear history
- `/remember <fact>` - Store information

### **Auto-Return Commands**

- `/smart_suggestions` - Get optimization tips
- `/extend_timeout <time>` - Extend tool session
- `/timeout_status` - Check remaining time
- `/return_to_default` - Return to Memory immediately
- `/auto_return_status` - View system status

### **Interactive Commands**

- `/jakey_engage` - Make Jakey actively engage
- `/jakey_disengage` - Stop Jakey's engagement
- `/create_bet <title> <options>` - Create betting pool
- `/trivia` - Start trivia game
- `/keno` - Generate keno numbers

### **Image Commands**

- `/generate_image <prompt>` - Generate AI images
- `/edit_image <prompt>` - Edit images with AI

### **Utility Commands**

- `/time` - Display current time
- `/remind <time> <message>` - Set personal reminder
- `/memory_debug` - Debug memory system
- `/memory_reindex` - Fix memory issues
- `/quickstart` - Show quickstart guide
- `/help` - Comprehensive help guide

### **Popular Tools**

- **Memory** - Personal information recall
- **ExaSearch** - Web search
- **CryptoPrice** - Live crypto prices
- **Engagement** - Active channel participation
- **GamblingGames** - Betting pools and trivia
- **Image Generation** - AI image creation and editing

- **CodeExecution** - Python code execution

### **Pro Tips**

- **Be specific** in your requests
- **Use natural language** - talk normally
- **Let tools auto-enable** - most tools are automatic
- **Use smart suggestions** for optimization
- **Set reminders** for important tasks
- **Debug memory** if something's not working
- **Use `/jakey_engage`** to invite Jakey into the conversation
- **Try `/create_bet` and `/trivia`** for interactive games
- **Generate images directly** with `/generate_image`
- **Monitor timeouts** with `/timeout_status`

---

**🎮 Have fun chatting with JakeyBot! Remember, it's designed to be entertaining, helpful, and slightly chaotic. Enjoy the ride! 🚀**
