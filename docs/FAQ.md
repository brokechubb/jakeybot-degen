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
- **Pollinations.AI models** for uncensored responses

You can change models using:

- `/ask` command with different providers
- `/model set:` command to stick with a specific model

---

### Q: When I switch models, why don't they remember what we discussed?

**A**: This is normal behavior! Your chat session gets divided per model provider:

- **OpenAI conversations** have their own memory
- **Claude conversations** have their own memory  
- **Gemini conversations** have their own memory
- **Pollinations.AI conversations** have their own memory

Each model maintains separate conversation contexts for optimal performance and privacy.

---

## 🔄 **Auto-Return System**

### Q: What is the auto-return system?

**A**: The auto-return system automatically manages tool usage for you:

- **Automatic Tool Activation**: Tools are automatically enabled when needed
- **Smart Timeout Management**: Tools return to Memory after configurable timeouts
- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Seamless Experience**: No manual tool management required

---

### Q: How do I extend the timeout for a tool?

**A**: Use the `/extend_timeout` command:

```
/extend_timeout 5m    # Add 5 minutes
/extend_timeout 2h    # Add 2 hours
/extend_timeout 30m   # Add 30 minutes
```

---

### Q: How do I check how much time is left on my current tool?

**A**: Use `/timeout_status` to see remaining time:

```
/timeout_status
```

This will show you the current tool and how much time is left before it auto-returns to Memory.

---

### Q: What are smart suggestions?

**A**: Smart suggestions provide personalized optimization tips:

```
/smart_suggestions
```

**Example suggestions:**

- "You've been using CodeExecution for 8 minutes. Consider extending with `/extend_timeout 5m`"
- "For image generation, try `/generate_image` directly - no tool switching needed!"
- "You're doing a lot of web searches. Consider using `/feature ExaSearch` for a longer session"

---

### Q: How do I return to Memory immediately?

**A**: Use `/return_to_default` to immediately return to the Memory tool:

```
/return_to_default
```

---

## 🎮 **Interactive Features**

### Q: How do I make Jakey actively engage in a channel?

**A**: Use the `/jakey_engage` command to make Jakey actively participate in the current channel:

```
/jakey_engage
```

This will make Jakey periodically interject with relevant comments and engage with the conversation.

---

### Q: How do I stop Jakey's active engagement?

**A**: Use `/jakey_disengage` to stop Jakey's active participation:

```
/jakey_disengage
```

---

### Q: How do I create a betting pool?

**A**: Use `/create_bet` with a title and options:

```
/create_bet "Who will win the game?" "Team A,Team B,Team C"
```

This creates an interactive betting pool where users can vote on the options.

---

### Q: How do I start a trivia game?

**A**: Use `/trivia` to start an interactive trivia game:

```
/trivia
```

Jakey will generate AI-powered trivia questions for the channel to answer.

---

### Q: How do I generate keno numbers?

**A**: Use `/keno` to generate random keno numbers:

```
/keno
```

---

## 🎨 **Image Generation**

### Q: How do I generate images?

**A**: Use `/generate_image` directly - no tool switching required:

```
/generate_image a cute cat playing with yarn
/generate_image futuristic city skyline at sunset
```

---

### Q: How do I edit images?

**A**: Use `/edit_image` with an attached image:

```
/edit_image add a hat to this person
/edit_image make this image more colorful
```

Attach the image you want to edit when using this command.

---

### Q: Do I need to enable a tool for image generation?

**A**: No! Image generation commands work directly without enabling any tools. Just use `/generate_image` or `/edit_image`.

---

## 🛠️ **Tools & Features**

### Q: How do I enable tools?

**A**: Most tools are now **auto-enabled** when needed! Just ask JakeyBot what you need:

```
"Check the price of Bitcoin"  # Auto-enables CryptoPrice
"Search for the latest AI news"  # Auto-enables ExaSearch
"Convert 100 USD to EUR"  # Auto-enables CurrencyConverter
```

For manual control, use `/feature <tool_name>`:

```
/feature Memory          # Enable Memory tool
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
- **🎮 Engagement** - Active channel participation
- **🎲 GamblingGames** - Betting pools and trivia
- **🎨 Image Generation** - AI image creation and editing

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

**A**: It depends on the model provider:

- **Gemini**: Free tier available with rate limits
- **OpenAI**: Requires API key with usage costs
- **Claude**: Requires API key with usage costs
- **Pollinations.AI**: Free tier available, optional API key for premium features

Check each provider's pricing for current rates.

---

### Q: What API keys do I need?

**A**: Required API keys depend on which features you want to use:

**Essential:**

- `OPENAI_API_KEY` - For OpenAI models
- `GEMINI_API_KEY` - For Gemini models
- `MONGO_DB_URL` - For database functionality

**Optional:**

- `EXA_API_KEY` - For web search (ExaSearch)
- `GITHUB_TOKEN` - For GitHub integration
- `YOUTUBE_DATA_v3_API_KEY` - For YouTube analysis
- `POLLINATIONS_API_KEY` - For Pollinations.AI premium features

---

### Q: How do I configure API keys?

**A**: Add your API keys to the `dev.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
MONGO_DB_URL=your_mongodb_url_here

# Optional
EXA_API_KEY=your_exa_key_here
GITHUB_TOKEN=your_github_token_here
YOUTUBE_DATA_v3_API_KEY=your_youtube_key_here
POLLINATIONS_API_KEY=your_pollinations_key_here
```

---

## 🧠 **Memory System**

### Q: How does the Memory system work?

**A**: The Memory system automatically remembers information about you:

- **Automatic Detection**: JakeyBot detects and remembers personal information
- **Natural Sharing**: Just share information naturally in conversation
- **Personal Recall**: JakeyBot can recall your preferences and details
- **Privacy Focused**: Information is stored per user and server

---

### Q: How do I manually store information in Memory?

**A**: Use the `/remember` command:

```
/remember My favorite color is blue
/remember I work as a software developer
/remember My birthday is March 15th
```

---

### Q: How do I check if Memory is working?

**A**: Use `/memory_debug` to check the Memory system status:

```
/memory_debug
```

This will show you if the system is working properly and display statistics.

---

### Q: What if Memory search isn't working?

**A**: Try `/memory_reindex` to fix search issues:

```
/memory_reindex
```

This rebuilds the search index and can resolve missing information problems.

---

## ⏰ **Reminders & Time**

### Q: How do I set a reminder?

**A**: Use `/remind` with natural language:

```
/remind time_in:1h message:Take a break
/remind time_in:tomorrow 10am message:Team meeting
/remind time_in:2d message:Pay rent
```

---

### Q: What time formats are supported?

**A**: Both simple and natural language formats:

**Simple:**

- `30m`, `1h`, `2d`, `1w`

**Natural Language:**

- `tomorrow 10am`
- `next week`
- `in 2 hours`
- `next Monday`

---

### Q: How do I check the current time?

**A**: Use `/time` to get the current time and timezone information:

```
/time
```

---

## 🚨 **Troubleshooting**

### Q: JakeyBot isn't responding to my messages

**A**: Check these common issues:

1. **Bot Status**: Make sure the bot is online (green indicator)
2. **Permissions**: Verify the bot has "Send Messages" permission
3. **Channel Access**: Ensure the bot can see the channel
4. **Try `/ask`**: Use `/ask <question>` for direct responses

---

### Q: Tools aren't working

**A**: Try these solutions:

1. **Auto-enablement**: Most tools are automatically enabled when needed
2. **Manual Enable**: Use `/feature <tool_name>` if auto-enablement fails
3. **API Keys**: Check if the tool requires an API key
4. **Server Admins**: Contact server administrators for configuration issues

---

### Q: Memory isn't working

**A**: Try these steps:

1. **Enable Memory**: Use `/feature Memory`
2. **Share Information**: Tell JakeyBot something about yourself
3. **Debug**: Use `/memory_debug` to check system status
4. **Reindex**: Use `/memory_reindex` to fix search issues

---

### Q: Auto-return system isn't working

**A**: Check these items:

1. **System Status**: Use `/auto_return_status` to check system health
2. **Database**: Ensure database connection is working
3. **Configuration**: Check environment variables
4. **Smart Suggestions**: Use `/smart_suggestions` for optimization tips

---

### Q: Image generation isn't working

**A**: Try these solutions:

1. **Direct Commands**: Use `/generate_image` or `/edit_image` directly
2. **API Keys**: Check if image generation models require API keys
3. **Attachments**: Make sure to attach images when using `/edit_image`
4. **Permissions**: Verify the bot can send images

---

## 🎭 **Personality & Behavior**

### Q: Why is JakeyBot so sarcastic?

**A**: JakeyBot is designed with a unique, unfiltered personality:

- **Direct and honest** - No sugar-coating
- **Crypto and gambling expert** - Knows about trading, betting, casinos
- **Internet culture savvy** - Uses modern slang and emojis
- **Slightly rude** - But in a fun, entertaining way

This is part of JakeyBot's character as the "degenerate gambling mascot" of the Courtyard.

---

### Q: Can I change JakeyBot's personality?

**A**: JakeyBot's personality is part of its core identity and cannot be changed by users. However, you can:

- **Use different models** for different response styles
- **Be specific in prompts** to get different types of responses
- **Contact server admins** for server-specific customization

---

## 🔒 **Privacy & Security**

### Q: What information does JakeyBot store?

**A**: JakeyBot stores:

- **Conversation context** - For better responses
- **Personal preferences** - To personalize your experience
- **Tool usage** - To improve functionality
- **Personal reminders** - Only visible to you

**JakeyBot does NOT store:**

- Sensitive personal information
- Passwords or credentials
- Private messages (unless explicitly shared)

---

### Q: How do I clear my conversation history?

**A**: Use `/sweep` to clear your conversation history:

```
/sweep
```

This will clear the current chat session but won't delete stored memories.

---

### Q: Is my data secure?

**A**: JakeyBot follows security best practices:

- **User isolation** - Each user's data is separate
- **Server isolation** - Data is separated by Discord server
- **Database security** - Uses secure MongoDB connections
- **API key protection** - Keys are stored securely in environment variables

---

## 📚 **Getting Help**

### Q: Where can I get more help?

**A**: Try these resources:

1. **Documentation**: Check the docs folder for detailed guides
2. **Help Commands**: Use `/help` and `/quickstart`
3. **Server Admins**: Contact your server administrators
4. **Community**: Join JakeyBot community servers
5. **Smart Suggestions**: Use `/smart_suggestions` for optimization tips

---

### Q: How do I report a bug?

**A**: Report bugs to your server administrators or through the community channels. Include:

- **What you were trying to do**
- **What happened instead**
- **Error messages** (if any)
- **Steps to reproduce** the issue

---

### Q: How do I suggest a new feature?

**A**: Feature suggestions can be made to:

- **Server administrators** for server-specific features
- **Community channels** for general feature requests
- **GitHub repository** for technical contributions

---

## 🎯 **Quick Reference**

### **Essential Commands**

- `/ask <question>` - Ask anything
- `/help` - Comprehensive help
- `/quickstart` - Getting started guide
- `/sweep` - Clear conversation history

### **Auto-Return Commands**

- `/smart_suggestions` - Get optimization tips
- `/extend_timeout <time>` - Extend tool session
- `/timeout_status` - Check remaining time
- `/return_to_default` - Return to Memory immediately

### **Interactive Commands**

- `/jakey_engage` - Make Jakey actively engage
- `/create_bet <title> <options>` - Create betting pool
- `/trivia` - Start trivia game
- `/keno` - Generate keno numbers

### **Image Commands**

- `/generate_image <prompt>` - Generate AI images
- `/edit_image <prompt>` - Edit images with AI

### **Memory Commands**

- `/remember <fact>` - Store information
- `/memory_debug` - Check system status
- `/memory_reindex` - Fix search issues

### **Utility Commands**

- `/time` - Current time
- `/remind <time> <message>` - Set reminder
- `/feature <tool>` - Enable tools

---

**💡 Pro Tip**: Use `/smart_suggestions` regularly to get personalized optimization tips for using JakeyBot more effectively!
