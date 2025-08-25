# Configuration

## Bot

This document defines the `dev.env` variables used to configure the Discord bot. To get started, copy `dev.env.template` file to `dev.env`.

- `TOKEN` - Set the Discord bot token, get one from [Discord Developer Portal](https://discord.com/developers/applications).
- `BOT_NAME` - Set the name of your bot (defaults to "Jakey Bot")
- `BOT_PREFIX` - Set the command prefix for the bot (defaults to "$")

## Database

for chat history and other settings, this may be required.

- `MONGO_DB_URL` - Connection string for MongoDB database server (for storing chat history and other persistent data)
- `MONGO_DB_NAME` - Name of the database (defaults to `jakey_prod_db`)
- `MONGO_DB_COLLECTION_NAME` - Name of the collection within the database (defaults to `jakey_prod_db_collection`)

## Generative AI features

- `GEMINI_API_KEY` - Set the Gemini API token, get one at [Google AI Studio](https://aistudio.google.com/app/apikey). If left blank, generative features powered by Gemini will be disabled.
- `OPENAI_API_KEY` - Set the OpenAI API key, obtain one from [OpenAI Platform](https://platform.openai.com/api-keys)
  - `OPENAI_API_ENDPOINT` - Sets the base URL if you use GPT-4o models outside of OpenAI platform (e.g. GitHub models marketplace)
    - Setting to non-openai endpoints that doesn't have GPT-4o and GPT-4o mini would not work.
- `ANTHROPIC_API_KEY` - Set the Anthropic API keys for Claude models. Obtain one from [the console](https://console.anthropic.com/settings/keys)
- `MISTRAL_API_KEY` - Set the Mistral API keys for Mistral models. Obtain one from [La Platforme](https://console.mistral.ai/api-keys/)
- `XAI_API_KEY` - Used to access XAI Grok 2 models. [Get an API key from XAI console](https://console.x.ai)
- `GROQ_API_KEY` - Used to access models from Groq such as Deepseek R1 distilled and LLaMA models [Groq Cloud Console](https://console.groq.com/keys)
- `OPENROUTER_API_KEY` - Set an OpenRouter API key to access models within `/openrouter` command and when the model `openrouter` is set.
- `HF_TOKEN` - HuggingFace inference token for accessing HuggingFace serverless-supported models
- `POLLINATIONS_API_KEY` - Set the Pollinations.AI API key for uncensored models and premium features. [Get an API key from Pollinations.AI](https://pollinations.ai/api). Optional - works without API key for basic features.

## API and Search tools

To use Google Search, Bing Search, and YouTube tools, you must set the following values:

- `CSE_SEARCH_ENGINE_CXID` - Google Custom Search Engine ID (REQUIRED) [Visit your search engines and copy your Search Engine ID](https://programmablesearchengine.google.com/controlpanel/all)
- `CSC_GCP_API_KEY` - Google Cloud Platform API key for Custom Search. [Enable this API for free](https://console.cloud.google.com/apis/library/customsearch.googleapis.com) and [Configure API keys with Custom Search APIs](https://console.cloud.google.com/apis/credentials)
- `BING_SUBSCRIPTION_KEY` - Bing Search API subscription key [Get free F1 key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
- `YOUTUBE_DATA_v3_API_KEY` - YouTube Data API key. [Enable this API](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
- `GITHUB_TOKEN` - Get one at <https://github.com/settings/personal-access-tokens> with public access, used for GitHub file tool.
- `EXA_API_KEY` - ExaSearch API key for web search capabilities. [Get an API key from Exa](https://exa.ai/). Optional - works without API key for basic features.

## Auto-Return System Configuration

### **Default Tool Setting**

- `DEFAULT_TOOL` - Set the default tool for all users (defaults to "Memory")
  - **Options**: Memory, ExaSearch, GitHub, YouTube, AudioTools, IdeationTools, CryptoPrice, CurrencyConverter, CodeExecution
  - **Recommended**: Memory (for personalized conversations)

### **Auto-Return Timeouts**

Configure timeout durations for different tools (in seconds):

```bash
# Auto-return timeout settings (in seconds)
AUTO_RETURN_TIMEOUT_EXASEARCH=180    # 3 minutes for web searches
AUTO_RETURN_TIMEOUT_CODEEXECUTION=600 # 10 minutes for code execution
AUTO_RETURN_TIMEOUT_IMAGEGEN=300     # 5 minutes for image generation
AUTO_RETURN_TIMEOUT_AUDIOTOOLS=480   # 8 minutes for audio processing
AUTO_RETURN_TIMEOUT_GITHUB=240       # 4 minutes for GitHub operations
AUTO_RETURN_TIMEOUT_YOUTUBE=240      # 4 minutes for YouTube analysis
AUTO_RETURN_TIMEOUT_DEFAULT=300      # 5 minutes default timeout
```

### **Smart Suggestions**

- `ENABLE_SMART_SUGGESTIONS` - Enable intelligent optimization tips (defaults to "true")
- `SMART_SUGGESTIONS_INTERVAL` - How often to show suggestions (in minutes, defaults to 10)

## Engagement System Configuration

### **Engagement Settings**

Configure Jakey's active participation in channels:

```bash
# Engagement system configuration
ENGAGEMENT_CHECK_INTERVAL=1200       # How often to check for engagement (20 minutes)
ENGAGEMENT_INTERJECTION_PROBABILITY=0.1  # Probability of interjecting (10%)
ENGAGEMENT_MAX_CHANNELS=50           # Maximum channels to engage in simultaneously
ENGAGEMENT_MIN_INTERVAL=300          # Minimum time between messages (5 minutes)
ENGAGEMENT_ENABLE_LOGGING=true       # Enable engagement activity logging
ENGAGEMENT_ENABLE_PERSISTENCE=true   # Save engagement settings to database
```

### **Engagement Permissions**

- `ENGAGEMENT_REQUIRED_PERMISSION` - Minimum permission level to engage Jakey (defaults to "manage_channels")
- `ENGAGEMENT_LIST_PERMISSION` - Permission level to view engagement list (defaults to "manage_guild")
- `ENGAGEMENT_ALLOW_MULTIPLE` - Allow multiple channels per guild (defaults to "true")

## Administrative

- `TEMP_DIR` - Path to store temporary uploaded/downloaded attachments for multimodal use. Defaults to `temp/` in the cuurent directory if not set. Files are always deleted on every execution regardless if its successful or not, or when the bot is restared or shutdown.

## Chat History Configuration

### `SHARED_CHAT_HISTORY`

**Purpose**: Controls whether chat history is shared across all members within a Discord guild (server).

**Values**:

- `true` - Chat history is shared guild-wide (all members see the same conversation context)
- `false` - Each user has their own private chat history (recommended)

**Default**: `false` (private per-user history)

**Example Configuration**:

```bash
# In your dev.env file
SHARED_CHAT_HISTORY=false  # Recommended: Private conversations
# SHARED_CHAT_HISTORY=true   # Not recommended: Shared guild history
```

#### **How It Works**

**When `SHARED_CHAT_HISTORY=true`**:

- All guild members share the same conversation context
- Bot remembers conversations across the entire guild
- Useful for collaborative bots where team context is important
- **⚠️ Privacy Risk**: All members can see each other's conversation history

**When `SHARED_CHAT_HISTORY=false` (Recommended)**:

- Each user has completely separate conversation history
- Bot treats each user as having private, independent conversations
- Conversations behave like private DMs regardless of guild setting
- **✅ Privacy**: Each user's conversations remain completely private

#### **Important Considerations**

**Why We Recommend `false`**:

1. **No Admin Controls**: The bot lacks administrative controls to manage guild-wide chat history
2. **Privacy Protection**: Users expect their conversations to remain private
3. **Context Separation**: Prevents conversation context pollution between users
4. **Compliance**: Better for privacy regulations and user expectations

**Limitations**:

- Setting to `false` does **NOT** immediately delete existing per-guild chat history
- You must manually manage existing shared history if you want to clear it
- The bot cannot selectively migrate or preserve specific conversation data

#### **Managing Existing Shared History**

If you're changing from `true` to `false` and want to clear existing shared history:

```bash
# Use the cleanup script to remove shared history
python scripts/cleanup_shared_history.py

# Or manually clear the database collection
# (Be careful - this will delete ALL chat history)
```

## Memory System Configuration

### **Memory Settings**

Configure the Memory tool behavior:

```bash
# Memory system configuration
MEMORY_ENABLE_AUTO_DETECTION=true    # Automatically detect and store personal information
MEMORY_EXPIRATION_DAYS=365           # How long to keep memories (default: 1 year)
MEMORY_MAX_MEMORIES_PER_USER=1000    # Maximum memories per user
MEMORY_ENABLE_CATEGORIZATION=true    # Automatically categorize memories
MEMORY_ENABLE_PRIORITY_SYSTEM=true   # Use priority system for memory recall
```

### **Memory Database**

- `MEMORY_COLLECTION_NAME` - Database collection for storing memories (defaults to "memories")
- `MEMORY_ENABLE_INDEXING` - Enable search indexing for better recall (defaults to "true")

## Image Generation Configuration

### **Image Generation Settings**

Configure AI image generation features:

```bash
# Image generation configuration
IMAGE_GENERATION_ENABLE_DIRECT_COMMANDS=true  # Enable /generate_image and /edit_image
IMAGE_GENERATION_DEFAULT_MODEL=pollinations::flux  # Default image generation model
IMAGE_GENERATION_MAX_SIZE=1024                # Maximum image size
IMAGE_GENERATION_QUALITY=high                 # Image quality setting
```

### **Supported Image Models**

- **Pollinations.AI**: `pollinations::flux`, `pollinations::kontext`, `pollinations::sdxl`
- **Gemini**: `gemini::gemini-2.0-flash-001` (for image generation)
- **OpenAI**: `openai::dall-e-3` (if available)

## Gambling Games Configuration

### **Gambling Games Settings**

Configure interactive gambling features:

```bash
# Gambling games configuration
GAMBLING_ENABLE_BETTING_POOLS=true   # Enable betting pool creation
GAMBLING_ENABLE_TRIVIA=true          # Enable trivia games
GAMBLING_ENABLE_KENO=true            # Enable keno number generation
GAMBLING_MAX_BETTING_POOLS=10        # Maximum active betting pools per guild
GAMBLING_TRIVIA_ROUNDS=5             # Default number of trivia rounds
GAMBLING_ENABLE_LEADERBOARDS=true    # Enable score tracking
```

## Performance Configuration

### **Rate Limiting**

Configure rate limits to prevent abuse:

```bash
# Rate limiting configuration
RATE_LIMIT_MESSAGES_PER_MINUTE=60    # Maximum messages per minute per user
RATE_LIMIT_COMMANDS_PER_MINUTE=30    # Maximum commands per minute per user
RATE_LIMIT_IMAGE_GENERATION_PER_HOUR=10  # Maximum image generations per hour per user
RATE_LIMIT_TOOL_USAGE_PER_HOUR=100   # Maximum tool usage per hour per user
```

### **Caching**

Configure caching for better performance:

```bash
# Caching configuration
CACHE_ENABLE=true                    # Enable response caching
CACHE_DURATION_MINUTES=30            # How long to cache responses
CACHE_MAX_SIZE=1000                  # Maximum cached items
CACHE_ENABLE_TOOL_RESULTS=true       # Cache tool results
```

## Security Configuration

### **API Key Security**

- **Never commit API keys** to version control
- **Use environment variables** for all sensitive data
- **Rotate API keys** regularly
- **Monitor API usage** for unusual activity

### **Database Security**

```bash
# Database security settings
DB_ENABLE_AUTHENTICATION=true        # Enable MongoDB authentication
DB_ENABLE_SSL=true                   # Enable SSL connections
DB_CONNECTION_POOL_SIZE=10           # Connection pool size
DB_MAX_RETRY_ATTEMPTS=3              # Maximum retry attempts
```

### **Bot Permissions**

Ensure the bot has the minimum required permissions:

- **Send Messages** - Required for bot responses
- **Read Message History** - Required for context
- **Attach Files** - Required for image generation
- **Use Slash Commands** - Required for command functionality
- **Manage Messages** - Optional, for message management

## Environment File Example

Here's a complete example of a `dev.env` file:

```bash
# Bot Configuration
TOKEN=your_discord_bot_token_here
BOT_NAME=Jakey Bot
BOT_PREFIX=$

# Database Configuration
MONGO_DB_URL=mongodb://localhost:27017/jakey_bot
MONGO_DB_NAME=jakey_prod_db
MONGO_DB_COLLECTION_NAME=jakey_prod_db_collection

# AI Model API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
POLLINATIONS_API_KEY=your_pollinations_api_key_here

# Tool API Keys
EXA_API_KEY=your_exa_api_key_here
GITHUB_TOKEN=your_github_token_here
YOUTUBE_DATA_v3_API_KEY=your_youtube_api_key_here

# Auto-Return Configuration
DEFAULT_TOOL=Memory
AUTO_RETURN_TIMEOUT_EXASEARCH=180
AUTO_RETURN_TIMEOUT_CODEEXECUTION=600
AUTO_RETURN_TIMEOUT_IMAGEGEN=300

# Engagement Configuration
ENGAGEMENT_CHECK_INTERVAL=1200
ENGAGEMENT_INTERJECTION_PROBABILITY=0.1
ENGAGEMENT_MAX_CHANNELS=50

# Memory Configuration
MEMORY_ENABLE_AUTO_DETECTION=true
MEMORY_EXPIRATION_DAYS=365

# Chat History
SHARED_CHAT_HISTORY=false

# Performance
RATE_LIMIT_MESSAGES_PER_MINUTE=60
CACHE_ENABLE=true

# Security
DB_ENABLE_AUTHENTICATION=true
DB_ENABLE_SSL=true
```

## Configuration Validation

Use the configuration validator to check your setup:

```bash
# Validate configuration
python scripts/config_validator.py

# Check security
python scripts/security_check.py

# Test database connection
python scripts/test_database.py
```

## Troubleshooting Configuration

### **Common Issues**

1. **API Key Errors**: Ensure all required API keys are set correctly
2. **Database Connection**: Verify MongoDB URL and authentication
3. **Permission Errors**: Check bot permissions in Discord
4. **Rate Limiting**: Adjust rate limits if users hit limits frequently

### **Configuration Scripts**

```bash
# Setup environment
python scripts/setup_env.py

# Validate configuration
python scripts/validate_config.py

# Test all features
python scripts/test_all_features.py
```

---

**⚠️ Security Note**: Never share your `dev.env` file or commit it to version control. Always use environment variables for sensitive data.
