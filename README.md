# Jakey Bot: Degen Edition 🎰

**Multi-model AI Discord bot** with over the top personality — access to **Google Gemini**, **OpenAI**, **Anthropic**, **Mistral**, **LLaMA**, **DeepSeek**, **Grok**, and **OpenRouter** models!

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

- **Multi-model support** (Gemini 2.5 Pro/Flash, GPT-5, Claude 4, DeepSeek V3/R1, Grok 3, LearnLM 2.0 Flash)
- **Real-time chat** with personality
- **Image generation & editing** (Gemini 2.0 Flash - **Recently Fixed!**)
- **Audio manipulation** (TTS, voice cloning, editing)
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

- `/ask` - Quick questions
- `/sweep` - Clear conversation
- `/model set` - Switch AI models
- `/summarize` - Channel insights
- `/mimic` - User impersonation
- `/feature` - Enable/disable tools (one at a time)

### New Utility Commands

- `/remindme <time> <message>` - Set personal reminders
- `/time` - Get current time and DST status
- `/date` - Get current date and timezone info
- `/memory_debug` - Debug memory system issues
- `/memory_reindex` - Reindex memory for better performance
- `/timeout_status` - Check remaining time before auto-return
- `/extend_timeout <time>` - Extend current tool session
- `/return_to_default` - Immediately return to default tool
- `/auto_return_status` - View auto-return system status
- `/smart_suggestions` - Get intelligent tool usage recommendations

### Special Capabilities

- **💰 Token Prices**: "What's BONK price?" → "💰 Current BONK: $0.000012 USD"
- **🎲 Gambling**: Expert casino & betting insights
- **🏈 Sports**: Analysis, odds, predictions
- **💸 Crypto**: Airdrops, tips, blockchain knowledge
- **🧠 Memory**: Automatically remembers and recalls user information across conversations
- **⏰ Reminders**: Personal reminder system with natural language time parsing

### Available Tools

- **🧠 Memory** - Automatic memory recall and information storage (**Recommended Default**)
- **💰 CryptoPrice** - Live Solana/Ethereum token prices
- **💱 CurrencyConverter** - Live currency conversion (170+ currencies)
- **🎨 ImageGen** - AI image generation & editing (**Recently Fixed!**)
- **🎵 AudioTools** - Audio creation & manipulation
- **📺 YouTube** - Video analysis & summarization
- **💻 CodeExecution** - Python code execution
- **🔍 ExaSearch** - Advanced web search
- **📊 GitHub** - Repository access
- **🎯 IdeationTools** - Creative brainstorming & file generation

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

### 🔧 Critical Fixes & Improvements (August 2025)

- **Image Editing Fixed!** - Resolved critical bugs preventing image generation/editing
- **Tool Execution** - Fixed Gemini API tool calling issues
- **Discord Attachments** - Improved URL handling for image editing
- **Python Compatibility** - Fixed audioop module issues with newer Python versions
- **Gemini API Enhanced** - Added quota retry logic and improved safety settings
- **Database Connection** - Shared database connection across all bot components for better performance
- **Security Improvements** - Removed dangerous admin execute command

### �� New Features

- **Personal Reminder System**: Set and manage personal reminders with `/remindme`
- **Time & Date Commands**: Get current time, date, and timezone information
- **Memory System Management**: Debug and reindex memory with `/memory_debug` and `/memory_reindex`
- **Auto-Return Tool Management**: Intelligent tool switching with automatic return to default after timeout
- **Smart Suggestions System**: Context-aware recommendations for tool usage optimization and workflow efficiency
- **⏰ Reminder System** - Personal reminders with natural language time parsing
- **🕐 Time Commands** - Current time and DST status display
- **🧠 Memory Debugging** - New commands to debug and fix memory system issues
- **🔄 Memory Reindexing** - Force reindex to fix search problems
- **🧠 Memory Tool** - Automatically remembers and recalls user information
- **🛠️ Management Scripts** - Comprehensive tool and AI model management
- **🔒 Enhanced Security** - Improved security checking and environment setup
- **📚 Better Documentation** - Comprehensive guides and troubleshooting
- **Tool Management System** - New script for managing default tools across users
- **Enhanced AI Chat** - Improved message handling and history management
- **New AI Models** - Added GPT-5, DeepSeek V3/R1, Grok 3, LearnLM 2.0 Flash
- **Default Tool Configuration** - Set preferred tools via environment variables

### 🎯 New AI Models Available

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

---

**🔒 Enhanced Security Fork** | **🎰 Degen Edition** | **💀 Unfiltered & Proud**
