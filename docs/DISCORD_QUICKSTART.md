# Discord Quickstart Guide

## Basic Commands

- `/help` - Comprehensive help and quickstart guide
- `/quickstart` - Step-by-step getting started guide
- Mention Jakey with your question
- `/feature <tool>` - Enable specific tools (Memory, CryptoPrice, etc.)
- `/model set <model>` - Switch AI models
- `/sweep` - Clear conversation history
- `/jakey_engage` - Make Jakey actively engage in the current channel
- `/jakey_disengage` - Stop Jakey's active engagement
- `/create_bet <title> <options>` - Create a new betting pool
- `/cancel_bet` - Cancel the current betting pool
- `/trivia` - Start a trivia game
- `/cancel_trivia` - Cancel the current trivia game
- `/keno` - Generate random keno numbers
- `/generate_image <prompt>` - Generate AI images
- `/edit_image <prompt>` - Edit images with AI

## 🔄 **Auto Tool Switch System** ⭐ **NEW FEATURE**

JakeyBot features an **intelligent auto tool switch system** that automatically enables the right tools when you need them!

### **🎯 How It Works**

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
```

### **🚀 Key Benefits**

- **✅ No Manual Tool Switching** - Tools enable automatically when needed
- **✅ Smart Timeout Management** - Tools return to Memory after optimal timeouts
- **✅ Intelligent Suggestions** - Get optimization tips with `/smart_suggestions`
- **✅ Seamless Experience** - Focus on your questions, not tool management

## 🛠️ Core Features

### **AI Chat & Memory**

- **Default Tool**: Memory (personalized conversations)
- **Tool Switching**: Use `/feature <tool>` to access specialized tools
- **Auto-Return**: Tools automatically return to Memory after timeout

### **🔄 One Tool at a Time System**

**Important**: JakeyBot can only use **one tool at a time**. This ensures optimal performance and prevents conflicts.

- **Current Tool**: Only one tool is active at any moment
- **Tool Switching**: Use `/feature <tool>` to switch between tools
- **Auto-Return**: After a timeout, tools automatically return to Memory
- **Smart Management**: The system intelligently manages tool transitions

### **Smart Tool Management**

- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Timeout Control**:
  - `/timeout_status` - Check remaining time
  - `/extend_timeout <time>` - Add more time (e.g., `5m`, `2h`)
  - `/return_to_default` - Switch back to Memory immediately
- **System Status**: `/auto_return_status` for overview

### **Popular Tools**

- **ExaSearch**: Web search and research
- **CodeExecution**: Run Python code
- **Engagement**: Active channel participation
- **GamblingGames**: Betting pools and trivia
- **Image Generation**: AI image creation and editing
- **CryptoPrice**: Live cryptocurrency prices
- **CurrencyConverter**: Currency conversion

## ⚡ Quick Workflows

### **Auto Tool Switch Examples**

```
User: "What's the weather like in Tokyo?"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Searches for current Tokyo weather]

User: "Calculate 15% of 250"
JakeyBot: 🔄 **Auto-enabled CodeExecution** - Jakey needed this tool to help you!
         "15% of 250 = 37.5"

User: "What's the latest on Solana?"
JakeyBot: 🔄 **Auto-enabled CryptoPrice** - Jakey needed this tool to help you!
         "💰 Current SOL: $98.45 USD"
```

### **Image Generation**

```
/generate_image a cute cat playing with yarn
```

*Direct image generation - no tool switching needed!*

### **Web Research**

```
User: "Search for latest AI developments 2025"
JakeyBot: 🔄 **Auto-enabled ExaSearch** - Jakey needed this tool to help you!
         [Searches web and provides results]
```

*Auto-returns to Memory in 3 minutes*

### **Code Execution**

```
User: "Run this python code: print('Hello World')"
JakeyBot: 🔄 **Auto-enabled CodeExecution** - Jakey needed this tool to help you!
         "Hello World"
```

*Auto-returns to Memory in 10 minutes*

### **Engagement & Games**

```
/jakey_engage
/create_bet "Who will win?" "Team A,Team B,Team C"
/trivia
```

*Interactive features for community engagement*

## 🧠 Smart Features

### **Personal Reminders**

```
/remindme 2h check the crypto prices
/remindme tomorrow 9am team meeting
```

### **Time & Date**

- `/time` - Current time and DST status
- `/date` - Current date and timezone

### **Memory Management**

- `/memory_debug` - Troubleshoot memory issues
- `/memory_reindex` - Optimize memory performance

### **Smart Suggestions**

- `/smart_suggestions` - Get personalized optimization tips
- `/extend_timeout 5m` - Extend tool session time
- `/timeout_status` - Check remaining time

## 🎮 Interactive Features

### **Engagement System**

- **Active Participation**: Jakey can actively engage in channels
- **Persistent Settings**: Engagement settings survive bot restarts
- **Smart Interjections**: Context-aware participation
- **Configurable Behavior**: Adjust engagement frequency and style

### **Gambling Games**

- **Betting Pools**: Create community betting pools
- **Trivia Games**: Interactive trivia with AI-generated questions
- **Keno Numbers**: Generate random keno numbers
- **Leaderboards**: Track scores and winners

### **Image Generation**

- **Direct Commands**: `/generate_image` and `/edit_image`
- **AI-Powered**: Uses advanced AI models for creation
- **No Tool Switching**: Works directly without enabling tools
- **Multiple Models**: Support for various image generation models

## 🔧 Advanced Usage

### **Tool Optimization**

- Use `/smart_suggestions` for personalized tips
- Extend sessions before timeouts
- Plan workflows to maximize tool usage

### **Customization**

- Tools auto-return to Memory (configurable default)
- Timeout durations optimized per tool type
- Activity-based intelligent suggestions

### **AI Model Selection**

- **Multiple Providers**: OpenAI, Gemini, Claude, Pollinations.AI
- **Specialized Models**: Text, image, audio, and reasoning models
- **Easy Switching**: Use `/model set` to change models
- **Model Information**: `/model list` to see all available models

## 🆘 Need Help?

- **Commands**: `/help` for full command list
- **Quick Reference**: `/quickstart` for this guide
- **Smart Tips**: `/smart_suggestions` for optimization advice
- **System Status**: `/auto_return_status` for tool management overview
- **Troubleshooting**: Check FAQ.md for common issues

## 💡 Pro Tips

1. **Use Memory First**: Start with Memory tool for personalized conversations
2. **Let Tools Auto-Enable**: Most tools are automatically enabled when needed
3. **Extend Timeouts**: Use `/extend_timeout` for longer sessions
4. **Get Smart Tips**: Use `/smart_suggestions` for workflow optimization
5. **Monitor Time**: Check `/timeout_status` to plan your work
6. **Plan Your Workflow**: Since only one tool works at a time, plan your tool usage sequence
7. **Use `/jakey_engage`** to invite Jakey into the conversation
8. **Try `/create_bet` and `/trivia`** for interactive games!
9. **Generate Images Directly**: Use `/generate_image` without tool switching
10. **Use Smart Suggestions**: Get personalized optimization advice

## 🎯 New Features (January 2025)

### **Auto-Return System**

- Tools automatically return to Memory after timeout
- Intelligent timeout management per tool type
- Smart suggestions for workflow optimization

### **Enhanced Engagement**

- Persistent engagement settings
- Configurable participation behavior
- Smart interjection system

### **Gambling Games**

- Community betting pools
- AI-generated trivia questions
- Interactive leaderboards

### **Direct Image Generation**

- No tool switching required
- Multiple AI models supported
- Advanced image editing capabilities

### **Smart Suggestions**

- Personalized optimization tips
- Workflow recommendations
- Performance insights

---

**🎯 That's it! Remember: one tool at a time for optimal performance!**
