# Jakey Bot: Degen Edition 🎰

**Multi-model AI Discord bot** with over the top personality — access to **Google Gemini**, **OpenAI**, **Anthropic**, **Mistral**, **LLaMA**, **DeepSeek**, **Grok**, **Pollinations.AI**, and **OpenRouter** models!

> **🔒 Enhanced Security Fork** | **🎰 Degenerate Gambler Edition** | **💀 Unfiltered Personality**

![Jakey Bot Banner](./assets/banner.png)

## 🚀 Quick Start

```bash
# 1. Set up environment securely
python scripts/setup_env.py

# 2. Configure API keys in dev.env

# 3. Verify security
python scripts/security_check.py

# 4. Start the bot
python main.py
```

## 📚 Documentation

- **[User Guide](./docs/DISCORD_USER_GUIDE.md)** - Complete user documentation
- **[Developer Guide](./docs/DEVELOPER_GUIDE.md)** - Technical documentation for developers
- **[API Reference](./docs/API.md)** - Comprehensive API documentation
- **[Configuration Guide](./docs/CONFIG.md)** - Setup and configuration
- **[Security Guide](./docs/SECURITY.md)** - Security best practices

## ⚠️ **Important: Python Version Compatibility**

**Currently Supported Python Versions:**

- ✅ **Python 3.11** - Full compatibility (Recommended)
- ⚠️ **Python 3.12** - Partial compatibility (Some features may not work)
- ❌ **Python 3.13** - Not compatible (audioop module removed)

**For best results, use Python 3.11:**

```bash
# Install Python 3.11
sudo pacman -S python311 python311-pip python311-venv

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
```

## ✨ Features

### 🤖 AI Capabilities

- **Multi-model support** (Gemini 2.5 Pro/Flash, GPT-5, Claude 4, DeepSeek V3/R1, Grok 3, LearnLM 2.0 Flash, Pollinations.AI)
- **Real-time chat** with personality
- **Image generation & editing** (Direct commands with multiple AI models)
- **Audio manipulation** (TTS, voice cloning, editing)
- **Voice channel music** (LavaLink v4 support)
- **Music playback** (YouTube, Spotify, and other sources)
- **Queue management** (play, pause, skip, volume control)
- **Vote-based skipping** (democratic music control)
- **Code execution** (Python)
- **Web search** & **YouTube analysis**

### 🎰 Online Gambling Specialties

- **💰 Live crypto prices** (Solana & Ethereum via Jupiter)
- **🎲 Gambling expertise** (casinos, odds, strategies)
- **🏈 Sports betting** (analysis, predictions, tips)
- **💸 Crypto knowledge** (airdrops, tips, blockchain)
- **🎰 Stake bonuses** (monthly predictions)

### 🛡️ Security Features

- **Enhanced .gitignore** (auto-excludes sensitive files)
- **Pre-commit hooks** (scans for API keys)
- **Security check script** (comprehensive scanning)
- **Environment setup** (secure configuration)
- **Removed dangerous commands** (admin execute command removed for security)

### ⚡ Performance Features

- **Intelligent Caching** (API responses, database queries, model instances)
- **Performance Monitoring** (real-time metrics and optimization recommendations)
- **Rate Limiting** (per-user and per-guild command limits)
- **Auto-Return System** (automatic tool switching and timeout management)
- **Database Optimization** (indexed queries and connection pooling)

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

### **⏰ Smart Timeouts**

Different tools have optimized timeout durations:

| Tool | Timeout | Use Case |
|------|---------|----------|
| **ExaSearch** | 3 minutes | Quick web searches |
| **CodeExecution** | 10 minutes | Complex calculations |
| **Image Generation** | 5 minutes | Image creation |
| **AudioTools** | 8 minutes | Audio processing |
| **Memory** | Default | Personal conversations |

### **🎮 Auto-Return Commands**

- `/smart_suggestions` - Get optimization tips
- `/extend_timeout <time>` - Extend current session (e.g., `5m`, `2h`)
- `/timeout_status` - Check remaining time
- `/return_to_default` - Return to Memory immediately
- `/auto_return_status` - View system overview

## 🎭 Jakey's Personality

**Rude, cocky, degenerate gambler** who talks like a **Zoomer/Gen Alpha**:

- **Cynical & Snarky** 💀 Unfiltered, offensive, proud of it
- **Crypto Expert** 💰 Blockchain, airdrops, token prices
- **Sports Betting Guru** 🏈 Odds, tips, predictions
- **Gambling Degenerate** 🎰 Casinos, games, degenerate status
- **Internet Culture** 🔥 Slang, emojis, casual vibes

**Example interactions:**

- "bro this is shit fr" → "bro really showed that pic i wish i could unsee 💀"
- "what teams u betting on?" → "chiefs takin it this year ez money"
- "best keno numbers?" → "doesn't matter keno gonna rinse u… but 1-10 if u feel spicy 🎰"

## 📋 Commands

### Core Commands

- `/help` - Comprehensive help and quickstart guide
- `/quickstart` - Step-by-step getting started guide
- `/ask` - Quick questions
- `/sweep` - Clear conversation
- `/model set` - Switch AI models (including Pollinations.AI)
- `/summarize` - Channel insights
- `/mimic` - User impersonation
- `/feature <tool>` - Enable/disable tools (one at a time)

### Auto-Return System Commands

- `/smart_suggestions` - Get optimization tips
- `/extend_timeout <time>` - Extend tool session time
- `/timeout_status` - Check remaining time
- `/return_to_default` - Return to Memory immediately
- `/auto_return_status` - View system status

### Interactive Commands

- `/jakey_engage` - Make Jakey actively engage in the current channel
- `/jakey_disengage` - Stop Jakey's active engagement
- `/create_bet <title> <options>` - Create a new betting pool
- `/cancel_bet` - Cancel the current betting pool
- `/trivia` - Start a trivia game
- `/cancel_trivia` - Cancel the current trivia game
- `/keno` - Generate random keno numbers

### Image Generation Commands

- `/play <query>` - Play music from YouTube, Spotify, or other sources
- `/pause` - Pause the current music
- `/resume` - Resume the paused music
- `/stop` - Stop playing and clear the queue
- `/skip` - Skip the current track (vote-based)
- `/queue` - Show the current music queue
- `/volume <level>` - Set the music volume (0-100)
- `/nowplaying` - Show information about the currently playing track
- `/disconnect` - Disconnect from the voice channel
- `/generate_image <prompt>` - Generate images using AI (no tool switching needed)
- `/edit_image <prompt>` - Edit existing images (attach image first)
- `/image_help` - Show image generation help

### Administrative Commands

- `/performance` - View bot performance metrics (Admin only)
- `/cache` - View cache statistics (Admin only)
- `/logs` - View recent bot logs (Admin only)

### Utility Commands

- `/remindme <time> <message>` - Set personal reminders
- `/time` - Get current time and DST status
- `/date` - Get current date and timezone info
- `/memory_debug` - Debug memory system issues
- `/memory_reindex` - Reindex memory for better performance

### Special Capabilities

- **💰 Token Prices**: "What's BONK price?" → "💰 Current BONK: $0.000012 USD"
- **🎲 Gambling**: Expert casino & betting insights
- **🏈 Sports**: Analysis, odds, predictions
- **💸 Crypto**: Airdrops, tips, blockchain knowledge
- **🧠 Memory**: Automatically remembers and recalls user information across conversations
- **⏰ Reminders**: Personal reminder system with natural language time parsing
- **🔄 Auto-Return**: Intelligent tool management with automatic activation
- **🎮 Engagement**: Active channel participation and community building
- **🎲 Games**: Interactive betting pools and trivia games

### Available Tools

- **🧠 Memory** - Automatic memory recall and information storage (**Default**)
- **💰 CryptoPrice** - Live Solana/Ethereum token prices
- **💱 CurrencyConverter** - Live currency conversion (170+ currencies)
- **🎨 ImageGen** - AI-powered image generation and editing
- **🎵 AudioTools** - Audio creation & manipulation
- **📺 YouTube** - Video analysis & summarization
- **💻 CodeExecution** - Python code execution
- **🔍 ExaSearch** - Advanced web search
- **📊 GitHub** - Repository access
- **🎯 IdeationTools** - Creative brainstorming & file generation
- **🎮 Engagement** - Active channel participation
- **🎲 GamblingGames** - Betting pools and trivia games

## 🔄 Auto-Return System

JakeyBot features an intelligent **auto-return system** that automatically manages tool usage:

### Key Features

- **Automatic Tool Activation**: Tools are automatically enabled when needed
- **Smart Timeout Management**: Tools return to Memory after configurable timeouts
- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Seamless Experience**: No manual tool management required

### How It Works

1. **Automatic Detection**: JakeyBot analyzes your request and determines which tool is needed
2. **Smart Timeout**: The system starts a countdown based on the tool type
3. **Intelligent Return**: After the timeout, the tool automatically returns to Memory
4. **Smart Suggestions**: The system learns from your usage patterns and provides optimization tips

### Timeout Durations

| Tool Type | Default Timeout | Use Case |
|-----------|----------------|----------|
| **Memory** | Default | Personal conversations |
| **ExaSearch** | 3 minutes | Quick web searches |
| **CodeExecution** | 10 minutes | Complex calculations |
| **Image Generation** | 5 minutes | Image creation |
| **AudioTools** | 8 minutes | Audio processing |

## 🎮 Interactive Features

### Engagement System

JakeyBot can actively participate in your channels:

- **Active Participation**: Jakey can actively engage in channels
- **Persistent Settings**: Engagement settings survive bot restarts
- **Smart Interjections**: Context-aware participation
- **Configurable Behavior**: Adjust engagement frequency and style

### Gambling Games

Interactive gambling and gaming features:

- **Betting Pools**: Create community betting pools
- **Trivia Games**: Interactive trivia with AI-generated questions
- **Keno Numbers**: Generate random keno numbers
- **Leaderboards**: Track scores and winners

## 🎨 Direct Image Generation

JakeyBot can generate images directly without tool switching:

- **Direct Commands**: `/generate_image` and `/edit_image`
- **AI-Powered**: Uses advanced AI models for creation
- **No Tool Switching**: Works directly without enabling tools
- **Multiple Models**: Support for various image generation models

## 🧠 Memory System

The bot now features an intelligent memory system that automatically remembers and recalls information across conversations:

### How It Works

- **Automatic Detection**: The bot automatically detects when users share personal information and stores it
- **Smart Recall**: When you ask questions, the bot searches its memory for relevant information
- **Natural Integration**: Memory recall happens seamlessly during normal conversations
- **Enhanced Database**: Shared database connection for better performance and reliability
- **Username Association**: All stored facts are prefixed with the username who shared them, preventing confusion between multiple users

### Examples

- **Sharing Info**: "My name is Jimmy" → Bot remembers and acknowledges
- **Recalling Info**: "What's my name?" → Bot recalls "Your name is Jimmy"
- **Preferences**: "I love pizza" → Bot remembers your food preference
- **Future Conversations**: Bot will remember your preferences even in new conversations
- **Multiple Users**: No confusion when multiple users share similar information (e.g., multiple users named "John" or who like "pizza")

### Manual Commands

- `/remember <fact>` - Manually store information
- `/feature Memory` - Enable the Memory tool for automatic operation
- `/memory_debug` - Check memory system status
- `/memory_reindex` - Fix search issues by reindexing

## ⏰ Reminder System

New personal reminder system with natural language time parsing:

### Usage

- **`/remind 1h take a break`** - Remind in 1 hour
- **`/remind 30m check crypto prices`** - Remind in 30 minutes  
- **`/remind tomorrow 10am daily standup`** - Remind tomorrow at 10 AM
- **`/remind 2d pay rent`** - Remind in 2 days

### Features

- **Natural Language**: Understands "1h", "30m", "tomorrow 10am", "next week"
- **Automatic Delivery**: Bot automatically sends reminders when due
- **Personal**: Each user's reminders are private and separate
- **Flexible**: Works with both slash commands and prefix commands

## 🆕 Latest Updates

### 🔧 Critical Fixes & Improvements (January 2025)

- **Auto-Return System**: Intelligent tool management with automatic activation and timeout management
- **Enhanced Engagement**: Persistent engagement settings with MongoDB storage and configurable behavior
- **Gambling Games**: Interactive betting pools, trivia games, and keno number generation
- **Direct Image Generation**: No tool switching required for image creation and editing
- **Pollinations.AI Integration**: New AI provider with uncensored models and premium features
- **Smart Suggestions**: Context-aware optimization tips for tool usage and workflow efficiency
- **Documentation Updates**: Comprehensive refresh of all documentation with latest features

### 🎯 New AI Models Available

- **Pollinations.AI**: Uncensored models (evil, unity), text models, image models
- **OpenAI**: GPT-5, GPT-5 Mini, O4 Mini
- **DeepSeek**: V3 (non-reasoning), R1 (reasoning) via Azure AI Foundry
- **xAI**: Grok 3 for creative tasks
- **Google**: LearnLM 2.0 Flash Experimental for learning tasks

## 🛠️ **New Management Scripts**

### **Tool Management**

```bash
# Check all tools status
python scripts/manage_tools.py

# Check specific tool
python scripts/manage_tools.py status Memory

# Set default tool for all users
python scripts/set_default_tool.py Memory
```

### **AI Model Management**

```bash
# Check all AI models status
python scripts/manage_ai_models.py

# Check specific model configuration
python scripts/manage_ai_models.py config openai
```

### **Setup & Testing**

```bash
# Set up Memory tool as default
python scripts/setup_memory.py

# Test Memory tool functionality
python scripts/test_memory.py

# Security verification
python scripts/security_check.py
```

## 🔒 Security Tools

### Quick Security Check

```bash
# Configure API keys securely in dev.env
# The bot includes built-in security features
# No additional scripts required
```

### Protection Features

- **🛡️ Auto-detection** of API keys & tokens
- **🚨 Pre-commit blocking** of sensitive files
- **📋 Comprehensive scanning** for credentials
- **📚 Security documentation** & guides
- **🚫 Removed dangerous commands** (admin execute command removed)

**Never commit `dev.env`** — it's automatically ignored!

## 🛠️ Installation

### Prerequisites

**Required Python Version: 3.11 (Recommended)**

```bash
# Install Python 3.11
sudo pacman -S python311 python311-pip python311-venv

# Verify installation
python3.11 --version
```

### Setup

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Verify Python version
python --version  # Should show Python 3.11.x

# Install dependencies
pip install -r requirements.txt

# Configure dev.env from template
cp dev.env.template dev.env
# Edit dev.env with your API keys
```

## 📚 Documentation

- **[CONFIG.md](./docs/CONFIG.md)** - Configuration guide
- **[SECURITY.md](./docs/SECURITY.md)** - Security best practices
- **[TOOLS.md](./docs/TOOLS.md)** - Tool documentation
- **[FAQ.md](./docs/FAQ.md)** - Frequently asked questions
- **[MEMORY_QUICKSTART.md](./docs/MEMORY_QUICKSTART.md)** - Memory tool guide
- **[AUTO_RETURN_GUIDE.md](./docs/AUTO_RETURN_GUIDE.md)** - Auto-return system guide
- **[🚀 DISCORD_QUICKSTART.md](./docs/DISCORD_QUICKSTART.md)** - **5-minute quick start for Discord users**
- **[🎮 DISCORD_USER_GUIDE.md](./docs/DISCORD_USER_GUIDE.md)** - **Complete user guide for Discord users**

## 🎯 Get Started

1. **Install Python 3.11** (required for compatibility)
2. **Set up environment** by copying `dev.env.template` to `dev.env`
3. **Configure API keys** in `dev.env`
4. **Install dependencies** with `pip install -r requirements.txt`
5. **Start the bot** with `python main.py`
6. **Start chatting** with Jakey's unique personality!

## 🆘 **Troubleshooting**

### **Python Version Issues**

```bash
# Check Python version
python --version

# If not 3.11, install and use Python 3.11
sudo pacman -S python311 python311-pip python311-venv
python3.11 -m venv venv
source venv/bin/activate
```

### **Common Issues**

- **audioop module errors** → Use Python 3.11
- **Tool not working** → Check bot logs and configuration
- **Memory not working** → Check database connection with `/memory_debug`
- **Reminders not working** → Check database connection with `/memory_debug`
- **Auto-return issues** → Check `/auto_return_status` for system overview
- **Image generation issues** → Use direct commands `/generate_image` and `/edit_image`

---

**🔒 Enhanced Security Fork** | **🎰 Degen Edition** | **💀 Unfiltered & Proud**
