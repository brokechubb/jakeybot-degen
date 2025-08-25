# 🛠️ JakeyBot Tools

JakeyBot has a powerful tool system that extends its functionality beyond text generation, similar to [ChatGPT plugins](https://openai.com/index/chatgpt-plugins/) or [Gemini Extensions](https://support.google.com/gemini/answer/13695044). These tools allow JakeyBot to interact with external services, perform specific tasks, and provide real-time information.

## 🔧 How Tools Work

Tools use **function calling** under the hood. When you ask JakeyBot a specific question that requires external functionality, it intelligently calls the appropriate tool by passing the function name and arguments from the tool's schema during the text completion process.

## 🚀 **Auto-Return System**

JakeyBot features an intelligent **auto-return system** that automatically manages tool usage:

- **Automatic Tool Activation**: Tools are automatically enabled when needed
- **Smart Timeout Management**: Tools return to Memory after configurable timeouts
- **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
- **Seamless Experience**: No manual tool management required

### **Auto-Return Commands**

- `/smart_suggestions` - Get personalized optimization tips
- `/extend_timeout <time>` - Extend current tool session (e.g., `5m`, `2h`)
- `/timeout_status` - Check remaining time on current tool
- `/return_to_default` - Immediately return to Memory tool
- `/auto_return_status` - View auto-return system status

## 📋 Available Tools

### 🧠 **Memory Tool** (Default)

**Purpose**: Automatically remember and recall information from previous conversations

**Features**:

- Store personal facts, preferences, and information
- Automatic categorization and organization
- Configurable expiration times
- Privacy-focused with user isolation
- **Auto-enabled** as default tool

**Use Cases**:

- Remembering user names and preferences
- Storing important information for future reference
- Building personalized user experiences

**Setup**:

```bash
# Set as default tool
python scripts/setup_memory.py

# Or enable per-guild
/feature Memory
```

---

### 🎨 **Image Generation & Editing**

**Purpose**: Create and modify images using AI

**Features**:

- Generate images from text descriptions
- Edit existing images with AI
- **Direct Commands**: `/generate_image` and `/edit_image`
- **No Tool Switching**: Works directly without enabling tools
- Multiple AI models supported (Pollinations.AI, Gemini, etc.)

**Use Cases**:

- Creating custom artwork
- Generating illustrations for content
- Modifying existing images

**Usage**:

```
/generate_image a cute cat playing with yarn
/edit_image add a hat to this person
```

---

### 🔍 **Web Search (ExaSearch)**

**Purpose**: Search the web for real-time information

**Features**:

- Real-time web search results
- Semantic search capabilities
- No rate limits on free tier
- Comprehensive result summaries
- **Auto-enabled** when needed

**Use Cases**:

- Finding current information
- Research and fact-checking
- Getting up-to-date news

**Setup**:

```bash
# Configure API key in dev.env
EXA_API_KEY=your_api_key_here

# Auto-enabled when needed
```

---

### 📚 **GitHub Integration**

**Purpose**: Access and analyze GitHub repositories

**Features**:

- Search repository files
- Analyze code and documentation
- Summarize README files and code
- Public repository access only
- **Auto-enabled** when needed

**Use Cases**:

- Understanding open-source projects
- Analyzing code structure
- Getting project summaries

**Setup**:

```bash
# Configure GitHub token in dev.env
GITHUB_TOKEN=your_github_token_here

# Auto-enabled when needed
```

---

### 🎥 **YouTube Search & Analysis**

**Purpose**: Search YouTube and analyze video content

**Features**:

- Search for videos based on queries
- Extract video metadata from URLs
- Get video information and statistics
- Real-time search results
- **Auto-enabled** when needed

**Use Cases**:

- Finding relevant videos
- Getting video information
- Research and content discovery

**Setup**:

```bash
# Configure YouTube API key in dev.env
YOUTUBE_DATA_v3_API_KEY=your_api_key_here

# Auto-enabled when needed
```

---

### 🎵 **Audio Tools**

**Purpose**: Manipulate and process audio files

**Features**:

- Voice cloning capabilities
- Audio file editing
- Format conversion
- Audio enhancement
- **Auto-enabled** when needed

**Use Cases**:

- Creating voice clones
- Editing audio content
- Audio file processing

**Setup**:

```bash
# Install dependencies
pip install gradio_client

# Auto-enabled when needed
```

---

### 💡 **Ideation Tools**

**Purpose**: Brainstorming and creative thinking

**Features**:

- **Canvas**: Create focused discussion threads
- **Artifacts**: Generate and share files (code, markdown, etc.)
- Thread-based organization
- File generation capabilities
- **Auto-enabled** when needed

**Use Cases**:

- Project planning and brainstorming
- Creating structured discussions
- Generating documentation and code

**Setup**:

```bash
# Auto-enabled when needed
```

---

### 💰 **Cryptocurrency Price Tool**

**Purpose**: Get real-time cryptocurrency prices

**Features**:

- Live price data for major cryptocurrencies
- Price comparisons and trends
- Market information
- No API key required
- **Auto-enabled** when needed

**Use Cases**:

- Checking crypto prices
- Market analysis
- Investment research

**Setup**:

```bash
# Auto-enabled when needed
```

---

### 💱 **Currency Converter**

**Purpose**: Convert between different currencies

**Features**:

- 170+ world currencies supported
- Live exchange rates
- Real-time conversion
- No API key required
- **Auto-enabled** when needed

**Use Cases**:

- Currency conversion
- Travel planning
- Financial calculations

**Setup**:

```bash
# Auto-enabled when needed
```

---

### 🐍 **Code Execution**

**Purpose**: Execute Python code and perform calculations

**Features**:

- Python code execution
- Mathematical calculations
- Data processing
- Gemini models only
- **Auto-enabled** when needed

**Use Cases**:

- Running calculations
- Testing code snippets
- Data analysis

**Setup**:

```bash
# Auto-enabled when needed
```

---

### 🎮 **Engagement System**

**Purpose**: Active channel participation and community engagement

**Features**:

- **Active Participation**: Jakey can actively engage in channels
- **Persistent Settings**: Engagement settings survive bot restarts
- **Smart Interjections**: Context-aware participation
- **Configurable Behavior**: Adjust engagement frequency and style
- **Commands**: `/jakey_engage`, `/jakey_disengage`

**Use Cases**:

- Community building
- Active channel participation
- Automated engagement

**Setup**:

```bash
# Enable engagement in a channel
/jakey_engage

# Disable engagement
/jakey_disengage
```

---

### 🎲 **Gambling Games**

**Purpose**: Interactive gambling and gaming features

**Features**:

- **Betting Pools**: Create community betting pools
- **Trivia Games**: Interactive trivia with AI-generated questions
- **Keno Numbers**: Generate random keno numbers
- **Leaderboards**: Track scores and winners
- **Commands**: `/create_bet`, `/trivia`, `/keno`

**Use Cases**:

- Community entertainment
- Interactive gaming
- Gambling-themed activities

**Setup**:

```bash
# Create a betting pool
/create_bet "Who will win?" "Team A,Team B,Team C"

# Start trivia
/trivia

# Generate keno numbers
/keno
```

## 🚀 Getting Started with Tools

### 1. **Auto-Enabled Tools**

Most tools are now **auto-enabled** when needed:

```
# Just ask - tools are automatically enabled
"Check the price of Bitcoin"
"Search for the latest AI news"
"Convert 100 USD to EUR"
```

### 2. **Manual Tool Management**

For specific tool usage:

```
/feature Memory          # Enable Memory tool
/feature ExaSearch       # Enable Web Search
```

### 3. **Check Tool Status**

View currently enabled tools:

```
/feature                 # Shows current tool status
```

### 4. **Smart Suggestions**

Get optimization tips:

```
/smart_suggestions       # Get personalized tips
```

## ⚙️ Tool Configuration

### Environment Variables

Some tools require API keys configured in your `dev.env` file:

```bash
# Required for various tools
EXA_API_KEY=your_exa_api_key
GITHUB_TOKEN=your_github_token
YOUTUBE_DATA_v3_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
POLLINATIONS_API_KEY=your_pollinations_api_key  # Optional
```

### Default Tool Setting

Set a default tool for all new users:

```bash
# In your dev.env file
DEFAULT_TOOL=Memory

# Or use the script
python scripts/set_default_tool.py Memory
```

## 🔒 Tool Management

### Scripts for Tool Management

Use the provided scripts for advanced tool management:

```bash
# Check all tools status
python scripts/manage_tools.py

# Set default tool for existing users
python scripts/set_default_tool.py <tool_name>

# Test specific tools
python scripts/test_memory.py
```

### Tool Status Monitoring

```bash
# View tool health and configuration
python scripts/manage_tools.py status Memory
python scripts/manage_tools.py status ExaSearch
```

## 📊 Tool Usage Statistics

Monitor tool usage across your bot:

```bash
# View database statistics
python scripts/manage_tools.py
```

This shows:

- Total users and guilds
- Tool distribution across users
- Usage patterns and trends

## 🚨 Important Limitations

### Current Restrictions

- **One tool per chat thread**: Only one tool can be active at a time
- **Tool switching**: Changing tools clears chat history
- **Model compatibility**: Some tools work with specific AI models only

### Best Practices

1. **Let tools auto-enable**: Most tools are automatically enabled when needed
2. **Use smart suggestions**: Get optimization tips with `/smart_suggestions`
3. **Monitor timeouts**: Check `/timeout_status` to plan your work
4. **Extend sessions**: Use `/extend_timeout` for longer sessions
5. **Test thoroughly**: Verify tool functionality before production use

## 🧪 Testing Tools

### Test Scripts

```bash
# Test Memory tool
python scripts/test_memory.py

# Check tool configuration
python scripts/manage_tools.py

# Verify security
python scripts/security_check.py
```

### Manual Testing

1. Ask relevant questions to trigger tool usage
2. Verify the tool is automatically enabled
3. Check that results are accurate and helpful
4. Test auto-return functionality

## 🔮 Future Enhancements

### Planned Improvements

- **Multi-tool support**: Use multiple tools simultaneously
- **Tool chaining**: Sequential tool execution
- **Advanced analytics**: Detailed usage insights
- **Custom tools**: User-defined tool creation
- **Tool marketplace**: Community-contributed tools

### Technical Improvements

- **Better error handling**: Graceful fallbacks for tool failures
- **Performance optimization**: Faster tool execution
- **Caching**: Intelligent result caching
- **Rate limiting**: Better API usage management

## 📚 Additional Resources

### Documentation

- **Configuration Guide**: `docs/CONFIG.md`
- **Memory Implementation**: `docs/MEMORY_IMPLEMENTATION.md`
- **Security Guide**: `docs/SECURITY.md`
- **Auto-Return Guide**: `docs/AUTO_RETURN_GUIDE.md`
- **Scripts Documentation**: `scripts/README.md`

### Examples

- **Memory Demo**: `examples/memory_demo.md`
- **Currency Converter Usage**: `examples/currency_converter_usage.md`

### Support

- **FAQ**: `docs/FAQ.md`
- **Troubleshooting**: Check individual tool sections above
- **Community**: Join JakeyBot community for help

## ✅ Tool Status Checklist

Before using tools in production:

- [ ] Required API keys configured
- [ ] Tools properly auto-enabled
- [ ] Dependencies installed (if required)
- [ ] Database connection working
- [ ] Tool functionality tested
- [ ] Security measures in place
- [ ] Documentation reviewed
- [ ] Auto-return system configured

---

*Tools are currently in beta and subject to change. Use with appropriate caution and testing.*
