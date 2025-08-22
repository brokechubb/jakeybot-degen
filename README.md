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

### Special Capabilities

- **💰 Token Prices**: "What's BONK price?" → "💰 Current BONK: $0.000012 USD"
- **🎲 Gambling**: Expert casino & betting insights
- **🏈 Sports**: Analysis, odds, predictions
- **💸 Crypto**: Airdrops, tips, blockchain knowledge

### Available Tools

- **💰 CryptoPrice** - Live Solana/Ethereum token prices
- **💱 CurrencyConverter** - Live currency conversion (170+ currencies)
- **🎨 ImageGen** - AI image generation & editing (**Recently Fixed!**)
- **🎵 AudioTools** - Audio creation & manipulation
- **📺 YouTube** - Video analysis & summarization
- **💻 CodeExecution** - Python code execution
- **🔍 ExaSearch** - Advanced web search
- **📊 GitHub** - Repository access
- **🎯 IdeationTools** - Creative brainstorming & file generation

## 🆕 Latest Updates

### 🔧 Critical Fixes (August 2025)

- **Image Editing Fixed!** - Resolved critical bugs preventing image generation/editing
- **Tool Execution** - Fixed Gemini API tool calling issues
- **Discord Attachments** - Improved URL handling for image editing

### 🚀 New Features

- **Tool Management System** - New script for managing default tools across users
- **Enhanced AI Chat** - Improved message handling and history management
- **New AI Models** - Added GPT-5, DeepSeek V3/R1, Grok 3, LearnLM 2.0 Flash
- **Default Tool Configuration** - Set preferred tools via environment variables

### 🎯 New AI Models Available

- **OpenAI**: GPT-5, GPT-5 Mini, O4 Mini
- **DeepSeek**: V3 (non-reasoning), R1 (reasoning) via Azure AI Foundry
- **xAI**: Grok 3 for creative tasks
- **Google**: LearnLM 2.0 Flash Experimental for learning tasks

## 🔒 Security Tools

### Quick Security Check

```bash
# Scan for sensitive data
python scripts/security_check.py

# Secure environment setup
python scripts/setup_env.py

# Manage default tools for all users
python scripts/set_default_tool.py <tool_name>
```

### Protection Features

- **🛡️ Auto-detection** of API keys & tokens
- **🚨 Pre-commit blocking** of sensitive files
- **📋 Comprehensive scanning** for credentials
- **📚 Security documentation** & guides

**Never commit `dev.env`** — it's automatically ignored!

## 🛠️ Installation

### Docker (Recommended)

```bash
docker pull zavocc/jakey:sugilite
docker run -it --env-file dev.env --rm zavocc/jakey:sugilite
```

### Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure dev.env from template
python scripts/setup_env.py
```

## 📚 Documentation

- **[CONFIG.md](./docs/CONFIG.md)** - Configuration guide
- **[SECURITY.md](./docs/SECURITY.md)** - Security best practices
- **[TOOLS.md](./docs/TOOLS.md)** - Tool documentation
- **[FAQ.md](./docs/FAQ.md)** - Frequently asked questions

## 🎯 Get Started

1. **Set up securely** with `python scripts/setup_env.py`
2. **Configure API keys** in `dev.env`
3. **Verify security** with `python scripts/security_check.py`
4. **Start chatting** with Jakey's unique personality!

---

**🔒 Enhanced Security Fork** | **🎰 Degen Edition** | **💀 Unfiltered & Proud**
