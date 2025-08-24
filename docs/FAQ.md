# ❓ Frequently Asked Questions (FAQ)

This document answers the most common questions about JakeyBot. If you don't find your answer here, check the other documentation files or reach out to the community.

## 🤖 **Bot Behavior & Responses**

### Q: How can I make JakeyBot answer responses in its pure form?

**A**: JakeyBot has a system instruction set that refers to itself, its features, and other knowledge with human-like response vibes. Currently, there's no option to change this as system instructions are part of the context history and are cached.

**Alternative**: You can use the `/ask` command for more direct responses or specify your preferred tone in your prompts.

---

### Q: What is the default model used?

**A**:

- **Gemini 2.5 Flash** for balanced chat experiences with thinking capability
- **GPT-4.1 mini** for OpenRouter-based chats
- **Gemini 2.5 Flash Nonthinking** for most commands like `/summarize` or message actions

You can change models using:

- `/ask` command with different providers
- `/model set:` command to stick with a specific model

---

### Q: When I switch models, why don't they remember what we discussed?

**A**: This is normal behavior! Your chat session gets divided per model provider:

- **OpenAI conversations** have their own memory
- **Claude conversations** have their own memory  
- **Gemini conversations** have their own memory

Each model maintains separate conversation contexts for optimal performance and privacy.

---

## 🛠️ **Tools & Features**

### Q: How do I enable tools?

**A**: Use the `/feature` command to enable specific tools:

```
/feature Memory          # Enable Memory tool
/generate_image         # Generate images directly
/feature ExaSearch       # Enable Web Search
/feature GitHub          # Enable GitHub integration
```

**Note**: Only one tool can be active per chat thread, and switching tools will clear your chat history.

---

### Q: What tools are available?

**A**: JakeyBot offers many tools:

- **🧠 Memory** - Remember and recall information

- **🔍 ExaSearch** - Web search capabilities
- **📚 GitHub** - Repository analysis
- **🎥 YouTube** - Video search and analysis
- **🎵 AudioTools** - Audio manipulation
- **💡 IdeationTools** - Brainstorming and file generation
- **💰 CryptoPrice** - Cryptocurrency prices
- **💱 CurrencyConverter** - Currency conversion
- **🐍 CodeExecution** - Python code execution

See `docs/TOOLS.md` for complete details.

---

### Q: How do I set a default tool for all users?

**A**: You can set a default tool in two ways:

**Option 1: Environment Variable**

```bash
# In your dev.env file
DEFAULT_TOOL=Memory
```

**Option 2: Script for Existing Users**

```bash
# Set Memory as default for all existing users
python scripts/set_default_tool.py Memory
```

---

## 🔑 **API Keys & Configuration**

### Q: Are models free to use?

**A**:

- **Gemini models**: Free with API key (no billing required)
- **OpenAI models**: Requires credits from [OpenAI](https://help.openai.com/en/articles/8264644-how-can-i-set-up-prepaid-billing)
- **Other models**: Purchase credits from [OpenRouter](https://openrouter.ai)

**Self-hosting**: Use your own paid API keys for full control and privacy.

---

### Q: What API keys do I need?

**A**: Required API keys depend on which features you want:

**Essential**:

- `DISCORD_TOKEN` - Your Discord bot token
- `MONGO_DB_URL` - MongoDB connection string

**AI Models**:

- `GEMINI_API_KEY` - For Gemini models
- `OPENAI_API_KEY` - For GPT models
- `ANTHROPIC_API_KEY` - For Claude models

**Tools**:

- `EXA_API_KEY` - For web search
- `GITHUB_TOKEN` - For GitHub integration
- `YOUTUBE_DATA_v3_API_KEY` - For YouTube search

See `docs/CONFIG.md` for complete configuration details.

---

### Q: How do I set up my environment?

**A**: Use the setup script:

```bash
# Create your environment file
python scripts/setup_env.py

# Edit dev.env with your actual API keys
# Then verify security
python scripts/security_check.py
```

---

## 📁 **File Support & Attachments**

### Q: What type of files can I provide with my prompts?

**A**: File support varies by model:

- **Gemini**: Images, Audio, Video, PDF
- **Anthropic/OpenRouter**: Images, PDF

**Note**: Files are automatically deleted after processing for privacy.

---

### Q: How do I use IdeationTools for file generation?

**A**:

1. Enable the tool: `/feature IdeationTools`
2. Ask JakeyBot to create files (code, markdown, etc.)
3. Ensure the bot has permission to send attachments
4. Files will be generated and shared in the chat

---

## 🏠 **Self-Hosting & DMs**

### Q: I get errors when using JakeyBot in DMs

**A**: You need to install the app first:

1. Go to JakeyBot's profile card
2. Tap "Add app"
3. Click "Try it yourself"
4. Then you can use `/ask` and `/sweep` commands in DMs

Without this, you'll get "Integration error" when using commands directly.

---

### Q: Why can't I use the ask command in other servers?

**A**: The `/ask` command has restrictions due to Discord's user-installable app limitations:

- **Works in**: DMs and authorized guilds
- **Doesn't work in**: Servers where JakeyBot isn't fully authorized

This is because the command uses `ctx.send` which isn't allowed with user-installable apps.

**Reference**: [Discord App Moderation](https://support.discord.com/hc/en-us/articles/23957313048343/Moderating-Apps-on-Discord#h_01HZQQQEADYVN2CM4AX4EZGKHM)

---

## 🧠 **Memory & Context**

### Q: How does the Memory tool work?

**A**: The Memory tool automatically:

1. **Detects** when you share personal information
2. **Stores** facts with automatic categorization
3. **Recalls** relevant information when you ask questions
4. **Maintains** privacy with user isolation

**Setup**: Run `python scripts/setup_memory.py` to enable it as default.

---

### Q: What information gets remembered?

**A**: The Memory tool remembers:

**✅ Personal Information**:

- Names and details
- Preferences and favorites
- Interests and hobbies
- Skills and expertise

**❌ Not Remembered**:

- Commands and instructions
- Temporary requests
- Non-personal information

---

## 🔒 **Privacy & Data Handling**

### Q: How is my data handled?

**A**:

- **Chat history**: Stored in MongoDB database (self-hosted)
- **Files**: Automatically deleted after processing
- **Privacy**: User isolation and guild separation
- **Training**: Your data is NOT used to train models

**Self-hosting**: Use your own paid API keys for full control and privacy.

---

### Q: Is my data secure?

**A**: JakeyBot implements several security measures:

- **Environment variables** for all sensitive data
- **Database isolation** by user and guild
- **File cleanup** after processing
- **Security scripts** to prevent credential exposure

**Recommendation**: Add authentication to your MongoDB database for production use.

---

## 🚨 **Troubleshooting**

### Q: Tools aren't working properly

**A**: Try these steps:

1. **Check tool status**: `/feature`
2. **Verify configuration**: `python scripts/manage_tools.py`
3. **Test specific tools**: `python scripts/test_memory.py`
4. **Check database**: Ensure MongoDB is running
5. **Restart bot**: After configuration changes

---

### Q: Bot isn't responding to commands

**A**: Common causes:

1. **Permissions**: Bot needs proper Discord permissions
2. **Configuration**: Check your `.env` file
3. **API keys**: Verify API keys are valid
4. **Database**: Ensure MongoDB connection works
5. **Restart**: Restart the bot after changes

---

### Q: Memory tool isn't remembering information

**A**: Troubleshooting steps:

1. **Enable tool**: `/feature Memory`
2. **Check configuration**: `python scripts/setup_memory.py`
3. **Verify database**: MongoDB connection and permissions
4. **Test functionality**: `python scripts/test_memory.py`
5. **Check model**: Ensure AI model supports tool calling

---

## 🔮 **Future Features**

### Q: Will you support locally hosted models like OLLAMA?

**A**: Yes, but not immediately. Current focus is on:

1. **Flagship models** that most people use
2. **OpenRouter models** for variety
3. **Stable, reliable** API-based models

Local model support will come in future versions.

---

### Q: What improvements are planned?

**A**: Planned enhancements include:

- **Multi-tool support** - Use multiple tools simultaneously
- **Local model support** - OLLAMA and other local models
- **Advanced analytics** - Better usage insights
- **Custom tools** - User-defined tool creation
- **Performance optimization** - Faster response times

---

## 📚 **Getting Help**

### Q: Where can I find more help?

**A**:

**Documentation**:

- `docs/CONFIG.md` - Configuration guide
- `docs/TOOLS.md` - Tools documentation
- `docs/SECURITY.md` - Security guide
- `scripts/README.md` - Scripts documentation

**Scripts**:

- `python scripts/manage_tools.py` - Tool management
- `python scripts/manage_ai_models.py` - AI model status
- `python scripts/security_check.py` - Security verification

**Community**: Join the JakeyBot community for support and updates.

---

### Q: How do I report bugs or request features?

**A**:

1. **Check existing issues** first
2. **Provide clear reproduction steps**
3. **Include relevant logs** (without sensitive data)
4. **Describe expected vs actual behavior**
5. **Mention your configuration** (without API keys)

---

## ✅ **Quick Setup Checklist**

Before using JakeyBot:

- [ ] Environment file configured (`python scripts/setup_env.py`)
- [ ] API keys set up in `dev.env`
- [ ] MongoDB connection working
- [ ] Security check passed (`python scripts/security_check.py`)
- [ ] Bot has proper Discord permissions
- [ ] Tools enabled as needed (`/feature <tool_name>`)
- [ ] Memory tool configured (`python scripts/setup_memory.py`)

---

*Need more help? Check the other documentation files or reach out to the community!*
