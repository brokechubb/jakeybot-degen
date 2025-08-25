# 📚 JakeyBot Documentation Index

Welcome to JakeyBot's comprehensive documentation! This index will help you find the information you need quickly and easily.

## 🚀 **Getting Started**

### **For Discord Users**

- **[🚀 DISCORD_QUICKSTART.md](./DISCORD_QUICKSTART.md)** - **5-minute quick start guide**
- **[🎮 DISCORD_USER_GUIDE.md](./DISCORD_USER_GUIDE.md)** - **Complete user guide with examples**

### **For Server Administrators**

- **[CONFIG.md](./CONFIG.md)** - **Configuration and environment setup**
- **[SECURITY.md](./SECURITY.md)** - **Security best practices and guidelines**

## 🛠️ **Technical Documentation**

### **Tools & Features**

- **[TOOLS.md](./TOOLS.md)** - **Comprehensive guide to all available tools**
- **[MEMORY_QUICKSTART.md](./MEMORY_QUICKSTART.md)** - **Memory tool setup and usage**
- **[MEMORY_IMPLEMENTATION.md](./MEMORY_IMPLEMENTATION.md)** - **Technical implementation details**
- **[AUTO_RETURN_GUIDE.md](./AUTO_RETURN_GUIDE.md)** - **Auto-return system and smart suggestions**

### **Security & Management**

- **[SECURITY.md](./SECURITY.md)** - **Security implementation and best practices**
- **[SECURITY_SUMMARY.md](./SECURITY_SUMMARY.md)** - **Security features overview**
- **[scripts/README.md](../scripts/README.md)** - **Management scripts documentation**

## 📖 **Reference Guides**

### **Configuration & Setup**

- **[CONFIG.md](./CONFIG.md)** - Environment variables, API keys, and configuration
- **[FAQ.md](./FAQ.md)** - Frequently asked questions and troubleshooting

### **Specialized Tools**

- **[CURRENCY_CONVERTER.md](./CURRENCY_CONVERTER.md)** - Currency conversion tool guide
- **[AUTO_IMAGE_TROUBLESHOOTING.md](./AUTO_IMAGE_TROUBLESHOOTING.md)** - Image generation troubleshooting

## 🎯 **Documentation by User Type**

### **🎮 Discord Users (End Users)**

**Start Here**: [🚀 DISCORD_QUICKSTART.md](./DISCORD_QUICKSTART.md)

**What You'll Learn:**

- How to chat with JakeyBot
- Using the Memory tool for personalization
- Generating images and getting information
- Understanding JakeyBot's personality
- Using engagement and gambling features
- Troubleshooting common issues

**Next Step**: [🎮 DISCORD_USER_GUIDE.md](./DISCORD_USER_GUIDE.md) for detailed information

---

### **🛠️ Server Administrators**

**Start Here**: [CONFIG.md](./CONFIG.md)

**What You'll Learn:**

- Setting up the bot securely
- Configuring API keys and environment
- Managing tools and AI models
- Security best practices
- Troubleshooting technical issues

**Essential Reading**: [SECURITY.md](./SECURITY.md) and [scripts/README.md](../scripts/README.md)

---

### **🔧 Developers & Contributors**

**Start Here**: [MEMORY_IMPLEMENTATION.md](./MEMORY_IMPLEMENTATION.md)

**What You'll Learn:**

- Technical architecture details
- Tool implementation patterns
- Database schema and data flow
- API integration details
- Future enhancement plans

## 📋 **Quick Reference**

### **Essential Commands for Users**

- `/ask <question>` - Ask anything
- `/feature <tool>` - Enable tools
- `/sweep` - Clear conversation
- `/remember <fact>` - Store information
- `/jakey_engage` - Make Jakey actively engage in the current channel
- `/jakey_disengage` - Stop Jakey's active engagement
- `/create_bet <title> <options>` - Create a new betting pool
- `/cancel_bet` - Cancel the current betting pool
- `/trivia` - Start a trivia game
- `/cancel_trivia` - Cancel the current trivia game
- `/keno` - Generate random keno numbers
- `/generate_image <prompt>` - Generate AI images
- `/edit_image <prompt>` - Edit images with AI
- `/smart_suggestions` - Get optimization tips
- `/extend_timeout <time>` - Extend tool session time
- `/timeout_status` - Check remaining time

### **Popular Tools**

- **🧠 Memory** - Personal information recall
- **🔍 ExaSearch** - Web search
- **💰 CryptoPrice** - Live crypto prices
- **🎲 GamblingGames** - Betting pools and trivia
- **🗣️ Engagement** - Active channel participation
- **🎨 Image Generation** - AI image creation and editing
- **🎵 AudioTools** - Audio manipulation and generation
- **📚 GitHub** - Repository analysis
- **🎥 YouTube** - Video summarization
- **💻 CodeExecution** - Python code execution

### **Management Scripts for Admins**

- `python scripts/setup_memory.py` - Set up Memory tool
- `python scripts/manage_tools.py` - Check tool status
- `python scripts/security_check.py` - Verify security
- `python scripts/set_default_tool.py <tool>` - Set default tool
- `pip install PyNaCl` - Install for voice support

## 🔍 **Finding Specific Information**

### **Looking for...**

**How to use a specific tool?**
→ Check [TOOLS.md](./TOOLS.md) for comprehensive tool documentation

**Memory tool not working?**
→ Start with [MEMORY_QUICKSTART.md](./MEMORY_QUICKSTART.md)

**Security concerns?**
→ Read [SECURITY.md](./SECURITY.md) and [SECURITY_SUMMARY.md](./SECURITY_SUMMARY.md)

**Configuration issues?**
→ Check [CONFIG.md](./CONFIG.md) and [FAQ.md](./FAQ.md)

**Troubleshooting help?**
→ [FAQ.md](./FAQ.md) has common issues and solutions

**New engagement features?**
→ Check the new commands like `/jakey_engage`, `/create_bet`, and `/trivia`!

**Auto-return system?**
→ Read [AUTO_RETURN_GUIDE.md](./AUTO_RETURN_GUIDE.md) for smart tool management

**Image generation issues?**
→ Check [AUTO_IMAGE_TROUBLESHOOTING.md](./AUTO_IMAGE_TROUBLESHOOTING.md)

## 🆘 **Getting Help**

### **For Users**

1. **Check the guides** above
2. **Ask server administrators** for server-specific issues
3. **Use `/feature` command** to see available tools
4. **Try `/ask` command** for general questions
5. **Explore new commands** like `/jakey_engage`, `/create_bet`, and `/trivia` for more interaction!
6. **Use `/smart_suggestions`** for optimization tips

### **For Administrators**

1. **Read the technical documentation** above
2. **Use management scripts** to diagnose issues
3. **Check security documentation** for best practices
4. **Review configuration guide** for setup issues
5. **Ensure `PyNaCl` is installed** for voice support.
6. **Verify API keys** for OpenAI, OpenRouter, and Azure Blob Storage in `dev.env`.

### **For Developers**

1. **Study implementation guides** for architecture understanding
2. **Use test scripts** to verify functionality
3. **Check security guidelines** before making changes
4. **Review tool patterns** for consistency
5. **Explore new cogs** `cogs/engagement.py` and `cogs/gambling_games.py` for implementation details.

## 📊 **Documentation Status**

| Document | Status | Last Updated | Target Audience |
|----------|--------|--------------|-----------------|
| DISCORD_QUICKSTART.md | ✅ Complete | January 2025 | End Users |
| DISCORD_USER_GUIDE.md | ✅ Complete | January 2025 | End Users |
| CONFIG.md | ✅ Complete | January 2025 | Administrators |
| TOOLS.md | ✅ Complete | January 2025 | All Users |
| SECURITY.md | ✅ Complete | January 2025 | Administrators |
| FAQ.md | ✅ Complete | January 2025 | All Users |
| MEMORY_QUICKSTART.md | ✅ Complete | January 2025 | All Users |
| MEMORY_IMPLEMENTATION.md | ✅ Complete | January 2025 | Developers |
| CURRENCY_CONVERTER.md | ✅ Complete | January 2025 | All Users |
| AUTO_RETURN_GUIDE.md | ✅ Complete | January 2025 | All Users |
| AUTO_IMAGE_TROUBLESHOOTING.md | ✅ Complete | January 2025 | All Users |
| README.md | ✅ Complete | January 2025 | All Users |

## 🔄 **Keeping Documentation Updated**

### **Recent Updates (January 2025)**

- ✅ **Added comprehensive engagement system documentation**
- ✅ **Updated gambling games and trivia features**
- ✅ **Added auto-return system and smart suggestions**
- ✅ **Updated AI model support (Pollinations.AI, new Gemini models)**
- ✅ **Added image generation troubleshooting guide**
- ✅ **Updated all documentation with new features**
- ✅ **Added management script references**
- ✅ **Improved troubleshooting sections**
- ✅ **Introduced new engagement features**: Active channel participation, betting pools, and trivia games
- ✅ **Updated `requirements.txt`** with `PyNaCl` for voice support
- ✅ **Resolved `cogs.misc` loading error** by removing conflicting help commands
- ✅ **Provided guidance** for API key and Azure Blob Storage configuration
- ✅ **Added auto-return system** with intelligent tool management
- ✅ **Enhanced help system** with comprehensive guides and troubleshooting

### **Documentation Maintenance**

- All guides are regularly updated with new features
- Security information is kept current with latest threats
- Examples are tested and verified for accuracy
- User feedback is incorporated into improvements

---

## 🎯 **Quick Navigation**

**🚀 New User?** → [DISCORD_QUICKSTART.md](./DISCORD_QUICKSTART.md)
**🎮 Need Help?** → [DISCORD_USER_GUIDE.md](./DISCORD_USER_GUIDE.md)
**🛠️ Setting Up?** → [CONFIG.md](./CONFIG.md)
**🔒 Security?** → [SECURITY.md](./SECURITY.md)
**❓ Questions?** → [FAQ.md](./FAQ.md)
**🧠 Memory Tool?** → [MEMORY_QUICKSTART.md](./MEMORY_QUICKSTART.md)
**🔄 Auto-Return?** → [AUTO_RETURN_GUIDE.md](./AUTO_RETURN_GUIDE.md)
**🎨 Images?** → [AUTO_IMAGE_TROUBLESHOOTING.md](./AUTO_IMAGE_TROUBLESHOOTING.md)

---

**📚 Happy reading! If you can't find what you're looking for, check the FAQ or ask for help from your server administrators.**
