# 🚀 JakeyBot DEGEN Edition

> **Advanced Discord Bot with AI Integration, Performance Monitoring, and Comprehensive Tooling**

[![Version](https://img.shields.io/badge/version-DEGEN.2.1.0-blue.svg)](https://github.com/your-repo/jakeybot-degen)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintainer](https://img.shields.io/badge/maintainer-CHUBB-red.svg)](mailto:thechubb16@gmail.com)

---

## 🎭 **About This Project**

**JakeyBot DEGEN Edition** represents a complete evolution of the original project, now under new ownership and development by **CHUBB**. This version has been significantly enhanced with advanced AI integration, improved architecture, and professional development standards.

### ✨ **What Makes DEGEN Edition Special**

- **🤖 Advanced AI Integration** - Pollinations.AI models with uncensored responses
- **⚡ Enhanced Architecture** - Performance monitoring and intelligent tool management
- **🎮 Rich Features** - Engagement systems, gambling games, and enhanced music capabilities
- **🔧 Professional Development** - Comprehensive testing, documentation, and maintenance
- **🌐 Community Focus** - Built for users who want more than just a basic Discord bot

---

## 🚀 **Quick Start Guide**

### **For New Users**

1. **[🚀 5-Minute Setup](./docs/DISCORD_QUICKSTART.md)** - Get up and running fast
2. **[🎮 Complete User Guide](./docs/DISCORD_USER_GUIDE.md)** - Master all features
3. **[❓ FAQ](./docs/FAQ.md)** - Find answers to common questions

### **For Server Administrators**

1. **[⚙️ Configuration Guide](./docs/CONFIG.md)** - Set up and configure the bot
2. **[🔒 Security Best Practices](./docs/SECURITY.md)** - Keep your server safe
3. **[🛠️ Management Scripts](./scripts/)** - Maintain and optimize your bot

### **For Developers**

1. **[🧠 Memory Implementation](./docs/MEMORY_IMPLEMENTATION.md)** - Understand the architecture
2. **[🔧 Tools Documentation](./docs/TOOLS.md)** - Integrate and extend functionality
3. **[📊 API Reference](./docs/API.md)** - Technical implementation details

---

## 🎯 **Core Features**

### **🤖 AI & Intelligence**

- **Pollinations.AI Integration** - Uncensored, powerful AI responses
- **Memory System** - Personalized conversations and information recall
- **Smart Tool Detection** - Automatic tool selection based on context
- **Multi-Model Support** - OpenAI, Anthropic, Google, and more

### **🎮 Engagement & Entertainment**

- **Active Channel Participation** - Jakey actively engages in conversations
- **Gambling Games** - Betting pools and trivia competitions
- **Keno System** - Random number generation for games
- **Music Player** - LavaLink v4 support with advanced features

### **🔍 Information & Tools**

- **Enhanced Web Search** - ExaSearch with caching and performance optimization
- **Cryptocurrency Prices** - Real-time crypto data and tracking
- **Currency Conversion** - Multi-currency support
- **Code Execution** - Safe Python code execution environment
- **Image Generation** - AI-powered image creation and editing

### **⚡ Performance & Management**

- **Auto-Return System** - Intelligent tool management with configurable timeouts
- **Performance Monitoring** - Real-time bot performance tracking
- **Rate Limiting** - Smart request management
- **Database Optimization** - Efficient data storage and retrieval

---

## 📋 **Essential Commands**

### **🎯 Core Interactions**

```
@Jakey DEGEN <your question>     - Chat with the AI
/feature <tool>                   - Enable specific tools
/sweep                            - Clear conversation history
/remember <fact>                  - Store information
```

### **🎮 Engagement Commands**

```
/jakey_engage                     - Start active participation
/jakey_disengage                  - Stop active participation
/create_bet <title> <options>     - Create betting pool
/trivia                           - Start trivia game
/keno                             - Generate keno numbers
```

### **🛠️ Tool Commands**

```
/generate_image <prompt>          - Create AI images
/edit_image <prompt>              - Edit existing images
/smart_suggestions                - Get optimization tips
/extend_timeout <time>            - Extend tool session
/timeout_status                   - Check remaining time
```

### **⚙️ Administrative**

```
/model set <model>                - Switch AI models
/model current                    - Show current model
/model list                       - List available models
```

---

## 🛠️ **Available Tools**

| Tool | Description | Status |
|------|-------------|---------|
| **🧠 Memory** | Personal information recall and storage | ✅ Active |
| **🔍 ExaSearch** | Enhanced web search with caching | ✅ Active |
| **💰 CryptoPrice** | Live cryptocurrency prices | ✅ Active |
| **💱 CurrencyConverter** | Multi-currency conversion | ✅ Active |
| **🎨 ImageGen** | AI image generation and editing | ✅ Active |
| **💻 CodeExecution** | Safe Python code execution | ✅ Active |
| **🎵 Music** | LavaLink v4 music system | ✅ Active |

---

## 🔧 **Installation & Setup**

### **Prerequisites**

- Python 3.8 or higher
- Discord Bot Token
- MongoDB database (optional but recommended)
- LavaLink v4 server (for music features)

### **Quick Installation**

```bash
# Clone the repository
git clone https://github.com/your-repo/jakeybot-degen.git
cd jakeybot-degen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp dev.env.template dev.env
# Edit dev.env with your configuration

# Run the bot
python main.py
```

### **Environment Configuration**

```bash
# Required
TOKEN=your_discord_bot_token
DEFAULT_TOOL=Memory

# Optional but recommended
MONGO_DB_URL=mongodb://your_connection_string
POLLINATIONS_API_KEY=your_api_key
ENABLE_VOICE_FEATURES=true
```

---

## 📚 **Documentation Index**

### **🚀 Getting Started**

- **[DISCORD_QUICKSTART.md](./docs/DISCORD_QUICKSTART.md)** - 5-minute setup guide
- **[DISCORD_USER_GUIDE.md](./docs/DISCORD_USER_GUIDE.md)** - Complete user manual
- **[CONFIG.md](./docs/CONFIG.md)** - Configuration and setup

### **🛠️ Tools & Features**

- **[TOOLS.md](./docs/TOOLS.md)** - Comprehensive tool documentation
- **[MEMORY_QUICKSTART.md](./docs/MEMORY_QUICKSTART.md)** - Memory system guide
- **[AUTO_RETURN_GUIDE.md](./docs/AUTO_RETURN_GUIDE.md)** - Auto-return system
- **[MUSIC_GUIDE.md](./docs/MUSIC_GUIDE.md)** - Music system setup

### **🔧 Technical Documentation**

- **[API.md](./docs/API.md)** - API reference and integration
- **[MEMORY_IMPLEMENTATION.md](./docs/MEMORY_IMPLEMENTATION.md)** - Architecture details
- **[AUTO_TOOL_SENSITIVITY.md](./docs/AUTO_TOOL_SENSITIVITY.md)** - Configuration guide

### **📖 Reference & Support**

- **[FAQ.md](./docs/FAQ.md)** - Frequently asked questions
- **[CHANGELOG.md](./docs/CHANGELOG.md)** - Version history and updates
- **[SECURITY.md](./docs/SECURITY.md)** - Security guidelines

---

## 🎯 **Use Cases**

### **🎮 Gaming Communities**

- Trivia games and betting pools
- Active channel engagement
- Random number generation
- Music playback during sessions

### **💼 Business Servers**

- Information retrieval and summarization
- Currency conversion and crypto tracking
- Code execution for development
- Memory system for team knowledge

### **🎨 Creative Communities**

- AI image generation and editing
- Creative writing assistance
- Music creation and playback
- Collaborative brainstorming

### **📚 Educational Servers**

- Research assistance and web search
- Code examples and execution
- Multi-language support
- Knowledge retention systems

---

## 🔄 **Recent Updates (DEGEN.2.1.0)**

### **🚀 Major Features**

- **Advanced AI Integration** - Pollinations.AI as primary provider
- **Enhanced Music System** - LavaLink v4 with advanced features
- **Engagement System** - Active channel participation
- **Gambling Games** - Betting pools and trivia competitions

### **⚡ Performance Improvements**

- **Auto-Return System** - Intelligent tool management
- **Enhanced Caching** - Improved response times
- **Performance Monitoring** - Real-time optimization
- **Database Optimization** - Efficient data handling

### **🛠️ Developer Experience**

- **Comprehensive Testing** - Unit and integration tests
- **Code Quality Tools** - MyPy, Pylint, Black, isort
- **Documentation** - Complete guides and references
- **Management Scripts** - Easy maintenance and updates

---

## 🤝 **Contributing**

We welcome contributions from the community! Here's how you can help:

### **🐛 Bug Reports**

- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include error logs and system information

### **💡 Feature Requests**

- Describe the desired functionality
- Explain the use case and benefits
- Consider implementation complexity

### **🔧 Code Contributions**

- Fork the repository
- Create a feature branch
- Follow the coding standards
- Submit a pull request

### **📚 Documentation**

- Improve existing guides
- Add missing information
- Fix typos and errors
- Create examples and tutorials

---

## 📄 **License & Legal**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### **Attribution**

- **Original Project**: JakeyBot (original authors)
- **Current Maintainer**: CHUBB (<thechubb16@gmail.com>)
- **Version**: DEGEN.2.1.0
- **License**: MIT License

---

## 🎯 **Quick Navigation**

| Need | Document |
|------|----------|
| **🚀 New User?** | [DISCORD_QUICKSTART.md](./docs/DISCORD_QUICKSTART.md) |
| **🎮 Need Help?** | [DISCORD_USER_GUIDE.md](./docs/DISCORD_USER_GUIDE.md) |
| **🛠️ Setting Up?** | [CONFIG.md](./docs/CONFIG.md) |
| **🔒 Security?** | [SECURITY.md](./docs/SECURITY.md) |
| **❓ Questions?** | [FAQ.md](./docs/FAQ.md) |
| **🧠 Memory Tool?** | [MEMORY_QUICKSTART.md](./docs/MEMORY_QUICKSTART.md) |
| **🔄 Auto-Return?** | [AUTO_RETURN_GUIDE.md](./docs/AUTO_RETURN_GUIDE.md) |
| **🎵 Music?** | [MUSIC_GUIDE.md](./docs/MUSIC_GUIDE.md) |

---

## 🌟 **Support the Project**

If you find JakeyBot DEGEN Edition useful, consider supporting the project:

- **⭐ Star the repository** on GitHub
- **🐛 Report bugs** and issues
- **💡 Suggest features** and improvements
- **📚 Improve documentation** and examples
- **🔧 Contribute code** and fixes

---

**🎭 Welcome to JakeyBot DEGEN Edition - Where AI meets entertainment!**

*Built with ❤️ by CHUBB*
