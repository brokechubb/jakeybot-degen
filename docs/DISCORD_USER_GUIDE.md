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
| `/ask` | Ask JakeyBot a question | `/ask What's the weather like?` |
| `/time` | Displays the current time and DST status | `/time` |
| `/remind` | Set a reminder for yourself | `/remind time_in:1h message:Take a break` |
| `/sweep` | Clear conversation history | `/sweep` |
| `/model set` | Switch AI models | `/model set gemini` |
| `/feature <tool>` | Enable/disable tools | `/feature Memory` |
| `/jakey_engage` | Make Jakey actively engage in the current channel | `/jakey_engage` |
| `/jakey_disengage` | Stop Jakey's active engagement | `/jakey_disengage` |
| `/create_bet` | Create a new betting pool | `/create_bet title:Super Bowl options:Chiefs,49ers` |
| `/cancel_bet` | Cancel the current betting pool | `/cancel_bet` |
| `/trivia` | Start a trivia game | `/trivia` |
| `/cancel_trivia` | Cancel the current trivia game | `/cancel_trivia` |

### **Help & Support Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Comprehensive help and quickstart guide | `/help` |
| `/quickstart` | Step-by-step getting started guide | `/quickstart` |
| `/memory_debug` | Debug memory system status | `/memory_debug` |
| `/memory_reindex` | Fix memory search issues | `/memory_reindex` |

### **New Utility Commands**

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

### **Creating Images**

JakeyBot can generate images from your descriptions using AI!

**Examples:**

```
You: "Generate a cute cat playing with a ball of yarn"
JakeyBot: [Generates and sends the image]

You: "Create a futuristic city skyline at sunset"
JakeyBot: [Creates the requested image]
```

### **Editing Images**

You can also edit existing images:

1. **Upload an image** to Discord
2. **Ask JakeyBot to edit it** (e.g., "Make this image more colorful")
3. **JakeyBot will process and return** the edited version

## 🔍 **Web Search & Information**

### **Real-Time Information**

JakeyBot can search the web for current information:

**Examples:**

```
You: "What's the latest news about AI?"
JakeyBot: [Searches web and provides current information]

You: "What's the weather in Tokyo right now?"
JakeyBot: [Gets real-time weather data]
```

### **YouTube Analysis**

Get information about YouTube videos:

**Examples:**

```
You: "Summarize this video: [YouTube URL]"
JakeyBot: [Analyzes and summarizes the video content]

You: "What are the main points of this tutorial?"
JakeyBot: [Extracts key information from the video]
```

## 💰 **Crypto & Financial Tools**

### **Live Crypto Prices**

Get real-time cryptocurrency prices:

**Examples:**

```
You: "What's the current price of Bitcoin?"
JakeyBot: "💰 Current BTC: $43,250 USD"

You: "How much is 100 SOL worth in USD?"
JakeyBot: [Converts and shows current value]
```

### **Currency Conversion**

Convert between 170+ world currencies:

**Examples:**

```
You: "Convert 1000 EUR to USD"
JakeyBot: "💱 1,000 EUR = 1,085 USD"

You: "What's 50,000 JPY in GBP?"
JakeyBot: [Shows conversion with current rates]
```

## 🎵 **Audio Tools**

### **Voice Cloning & Audio Editing**

JakeyBot can help with audio manipulation:

**Examples:**

```
You: "Clone my voice saying 'Hello World'"
JakeyBot: [Processes and returns audio file]

You: "Edit this audio to remove background noise"
JakeyBot: [Processes uploaded audio file]
```

## 💻 **Code Execution**

### **Python Code Running**

JakeyBot can execute Python code for you:

**Examples:**

```
You: "Calculate the factorial of 10"
JakeyBot: [Runs Python code and returns result]

You: "Generate a random password"
JakeyBot: [Executes code to create password]
```

## 🎯 **Pro Tips & Best Practices**

### **Getting Better Responses**

1. **Be specific** - "Generate a red sports car" vs "make a car"
2. **Provide context** - "I need this for a presentation about AI"
3. **Use natural language** - Talk to JakeyBot like a person

### **Tool Usage**

- **One tool at a time** - Only one tool can be active per conversation
- **Switching tools** - Use `/feature <tool_name>` to change tools
- **Tool status** - Check what's enabled with `/feature`

### **Memory Optimization**

- **Share information naturally** - Don't force it
- **Be consistent** - Use the same terms for things
- **Update preferences** - Tell JakeyBot when things change

### **Reminder Best Practices**

- **Use natural language**: "tomorrow 10am" vs "24h"
- **Be specific**: "pay rent" vs "reminder"
- **Set reasonable times**: Avoid very short or very long reminders

## 🚨 **Troubleshooting**

### **Common Issues**

**JakeyBot not responding:**

- Check if the bot is online
- Verify bot has proper permissions
- Try using `/ask` command

**Tool not working:**

- Enable the tool with `/feature <tool_name>`
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

### **Getting Help**

1. **Check bot status** - Look for the green "Online" indicator
2. **Verify permissions** - Bot needs Send Messages, Read Message History
3. **Ask server admins** - They can check bot configuration
4. **Use `/feature`** - See what tools are available
5. **Debug memory** - Use `/memory_debug` for memory issues

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

### **Custom Tool Combinations**

While only one tool can be active at a time, you can:

1. **Use Memory tool** for personalization
2. **Use image generation commands** for image creation
3. **Use ExaSearch** for web research
4. **Return to Memory** to continue personalized conversations

### **Model Switching**

Different AI models have different strengths:

- **Gemini** - Great for general chat and creativity
- **GPT-4** - Excellent for analysis and reasoning
- **Claude** - Strong for writing and explanation
- **Specialized models** - For specific tasks

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

- `/ask <question>` - Ask anything
- `/feature <tool>` - Enable tools
- `/sweep` - Clear history
- `/remember <fact>` - Store information

### **New Utility Commands**

- `/time` - Display current time
- `/remind <time> <message>` - Set personal reminder
- `/memory_debug` - Debug memory system
- `/memory_reindex` - Fix memory issues
- `/quickstart` - Show quickstart guide

### **Popular Tools**

- **Memory** - Personal information recall

- **ExaSearch** - Web search
- **CryptoPrice** - Live crypto prices
- **Engagement** - Active channel participation
- **GamblingGames** - Betting pools and trivia

### **Pro Tips**

- **Be specific** in your requests
- **Use natural language** - talk normally
- **Enable Memory tool** for personalization
- **Switch tools** based on what you need
- **Set reminders** for important tasks
- **Debug memory** if something's not working
- **Use `/jakey_engage`** to invite Jakey into the conversation
- **Try `/create_bet` and `/trivia`** for interactive games!

---

**🎮 Have fun chatting with JakeyBot! Remember, it's designed to be entertaining, helpful, and slightly chaotic. Enjoy the ride! 🚀**
