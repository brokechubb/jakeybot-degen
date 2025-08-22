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

## API and Search tools

To use Google Search, Bing Search, and YouTube tools, you must set the following values:

- `CSE_SEARCH_ENGINE_CXID` - Google Custom Search Engine ID (REQUIRED) [Visit your search engines and copy your Search Engine ID](https://programmablesearchengine.google.com/controlpanel/all)
- `CSC_GCP_API_KEY` - Google Cloud Platform API key for Custom Search. [Enable this API for free](https://console.cloud.google.com/apis/library/customsearch.googleapis.com) and [Configure API keys with Custom Search APIs](https://console.cloud.google.com/apis/credentials)
- `BING_SUBSCRIPTION_KEY` - Bing Search API subscription key [Get free F1 key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
- `YOUTUBE_DATA_v3_API_KEY` - YouTube Data API key. [Enable this API](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
- `GITHUB_TOKEN` - Get one at <https://github.com/settings/personal-access-tokens> with public access, used for GitHub file tool.

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

**Option 1: Complete Database Reset (⚠️ DANGEROUS)**

```bash
# This will delete ALL data for ALL users
python scripts/flush_db.py
```

**Option 2: Manual Database Management**

1. Use MongoDB tools to manually manage collections
2. Reference the [HistoryManagement class](../core/ai/history.py) for implementation details
3. Consider backing up data before making changes

**Option 3: Gradual Migration**

1. Set `SHARED_CHAT_HISTORY=false`
2. New users will automatically get private history
3. Existing shared history remains but is no longer updated
4. Users can continue using existing context until manually cleared

#### **Use Case Examples**

**Set to `true` when**:

- Building a collaborative team bot
- All guild members need shared context
- Privacy is not a concern
- Bot is used for team coordination

**Set to `false` when**:

- Building a personal assistant bot
- User privacy is important
- Bot serves individual users independently
- Compliance with privacy regulations is required

#### **Configuration Best Practices**

1. **Start with `false`** for most use cases
2. **Test thoroughly** before deploying to production
3. **Document the setting** for your team and users
4. **Consider data migration** if changing from shared to private
5. **Monitor user feedback** after making changes

#### **Related Scripts and Tools**

```bash
# Check current database status
python scripts/manage_tools.py

# View tool usage statistics
python scripts/manage_tools.py

# Clear all data (⚠️ DANGEROUS - use with caution)
python scripts/flush_db.py

# Set default tool for new users
python scripts/set_default_tool.py Memory
```

#### **Troubleshooting**

**Common Issues**:

- **"Bot remembers other users' conversations"**: Check if `SHARED_CHAT_HISTORY` is set to `true`
- **"Conversation context is lost"**: Verify the setting matches your intended behavior
- **"Database errors"**: Ensure MongoDB connection is properly configured

**Debugging**:

- Check your `.env` file for the correct setting
- Verify the bot has been restarted after changing the setting
- Use the management scripts to check current status

# Default Tool Configuration

## Setting Default Tools

You can configure JakeyBot to enable specific tools by default for all new users/guilds. This is useful if you want certain capabilities (like image generation) to be available without users having to manually enable them.

### Method 1: Environment Variable (Recommended)

Add the `DEFAULT_TOOL` environment variable to your `dev.env` file:

```bash
# Default tool to enable for new users/guilds
# Options: ImageGen, ExaSearch, GitHub, YouTube, AudioTools, IdeationTools, CryptoPrice, CurrencyConverter, CodeExecution, or None to disable
DEFAULT_TOOL=ImageGen
```

### Method 2: Update Existing Users

To set a default tool for all existing users/guilds in your database, use the provided script:

```bash
# Enable ImageGen for all users
python scripts/set_default_tool.py ImageGen

# Enable web search for all users
python scripts/set_default_tool.py ExaSearch

# Disable all tools for all users
python scripts/set_default_tool.py None
```

### Available Tools

- **ImageGen** - Image generation and editing with Gemini 2.0 Flash
- **ExaSearch** - Web search using Exa API
- **GitHub** - GitHub repository access and file analysis
- **YouTube** - YouTube search and video analysis
- **AudioTools** - Audio manipulation and voice cloning
- **IdeationTools** - Canvas and artifacts for brainstorming
- **CryptoPrice** - Live crypto token prices
- **CurrencyConverter** - Live currency conversion between 170+ currencies
- **CodeExecution** - Python code execution (Gemini only)
- **None** - Disable all tools

### Notes

- Setting a default tool only affects **new users/guilds** that haven't used the bot before
- Existing users will keep their current tool settings
- Users can still change their tool preference using the `/feature` command
- The default tool setting is stored per user/guild in the MongoDB database
