# 🔌 JakeyBot API Documentation

Comprehensive API reference for JakeyBot's internal services, tools, and integrations.

## 📋 Table of Contents

1. [Core Services](#core-services)
2. [AI Models](#ai-models)
3. [Tools](#tools)
4. [Database](#database)
5. [Caching](#caching)
6. [Performance Monitoring](#performance-monitoring)
7. [Error Handling](#error-handling)

## 🏗️ Core Services

### Database Manager

**Location**: `core/services/database_manager.py`

**Purpose**: Manages MongoDB connections and operations

```python
from core.services.database_manager import DatabaseManager

# Initialize
db = DatabaseManager()

# Basic operations
await db.insert_one("collection_name", {"key": "value"})
await db.find_one("collection_name", {"key": "value"})
await db.update_one("collection_name", {"key": "value"}, {"$set": {"new_key": "new_value"}})
await db.delete_one("collection_name", {"key": "value"})

# Bulk operations
await db.insert_many("collection_name", [{"key": "value1"}, {"key": "value2"}])
await db.find("collection_name", {"key": "value"})  # Returns cursor
```

**Methods**:

- `insert_one(collection, document)` - Insert single document
- `insert_many(collection, documents)` - Insert multiple documents
- `find_one(collection, filter)` - Find single document
- `find(collection, filter)` - Find multiple documents
- `update_one(collection, filter, update)` - Update single document
- `update_many(collection, filter, update)` - Update multiple documents
- `delete_one(collection, filter)` - Delete single document
- `delete_many(collection, filter)` - Delete multiple documents
- `create_index(collection, index)` - Create database index

### Cache Manager

**Location**: `core/services/cache_manager.py`

**Purpose**: Provides intelligent caching for API responses and database queries

```python
from core.services.cache_manager import api_cache, db_cache, model_cache, cached

# Direct cache operations
api_cache.set("key", "value", ttl=300)  # 5 minutes
value = api_cache.get("key")
api_cache.delete("key")
api_cache.clear()

# Cache decorator
@cached(ttl=300, cache_instance=api_cache)
async def expensive_function(parameter: str):
    # This result will be cached for 5 minutes
    return expensive_operation(parameter)

# Cache statistics
from core.services.cache_manager import cache_stats
stats = cache_stats()
print(f"Hit rate: {stats['api_cache']['hit_rate']:.2%}")
```

**Cache Instances**:

- `api_cache` - API responses (5 min TTL)
- `db_cache` - Database queries (10 min TTL)
- `model_cache` - Model instances (30 min TTL)

### Performance Monitor

**Location**: `core/services/performance_monitor.py`

**Purpose**: Monitors and reports on system performance

```python
from core.services.performance_monitor import get_performance_summary

# Get performance summary
summary = get_performance_summary()

# System metrics
system_stats = summary.get("system", {})
cpu_percent = system_stats.get("current_cpu_percent", 0)
memory_percent = system_stats.get("current_memory_percent", 0)
uptime = system_stats.get("uptime_formatted", "Unknown")

# Command metrics
command_stats = summary.get("commands", {})
total_commands = command_stats.get("total_commands", 0)
avg_response_time = command_stats.get("avg_response_time", 0)
```

## 🤖 AI Models

### Base Model Interface

**Location**: `aimodels/_template_/infer.py`

All AI models implement this interface:

```python
class Completions(ModelParams):
    def __init__(self, model_name, discord_ctx, discord_bot, guild_id=None):
        super().__init__()
        self._model_name = model_name
        self._discord_ctx = discord_ctx
        self._discord_bot = discord_bot
        self._guild_id = guild_id
    
    async def completion(self, conversation, return_text=True):
        """Main completion method - must be implemented"""
        raise NotImplementedError
    
    async def save_to_history(self, db_conn, chat_thread=None):
        """Save conversation to database"""
        # Default implementation provided
        pass
```

### OpenAI Integration

**Location**: `aimodels/openai/infer.py`

```python
from aimodels.openai.infer import Completions

# Initialize
model = Completions("pollinations::openai", ctx, bot, guild_id)

# Generate completion
response = await model.completion([
    {"role": "user", "content": "Hello, how are you?"}
])

# With tools
response = await model.completion(
    conversation,
    return_text=False,  # Return structured response
    tools=[tool_schema]
)
```

**Supported Models**:

- `pollinations::openai` - Text generation using OpenAI GPT-4.1 Nano via Pollinations.AI
- `pollinations::openai-fast` - Fast text generation using OpenAI GPT-4.1 Nano

### Gemini Integration

**Location**: `aimodels/gemini/infer.py`

```python
from aimodels.gemini.infer import Completions

# Initialize
model = Completions("pollinations::evil", ctx, bot, guild_id)

# Generate completion
response = await model.completion([
    {"role": "user", "content": "Hello, how are you?"}
])

# With image input
response = await model.completion([
    {"role": "user", "content": "Describe this image", "parts": [image_part]}
])
```

**Supported Models**:

- `pollinations::evil` - Uncensored text model
- `pollinations::unity` - Uncensored model with vision support
- `pollinations::openai` - Text generation using OpenAI GPT-4.1 Nano
- `pollinations::openai-fast` - Fast text generation using OpenAI GPT-4.1 Nano
- `pollinations::mistral` - Text generation using Mistral Small 3.1 24B
- `pollinations::gemini` - Text generation using Gemini 2.5 Flash Lite
- `pollinations::flux` - Image generation using Flux model
- `pollinations::kontext` - Image-to-image generation using Kontext model
- `pollinations::sdxl` - Image generation using Stable Diffusion XL

### Pollinations.AI Integration

**Location**: `aimodels/pollinations/infer.py`

```python
from aimodels.pollinations.infer import Completions

# Initialize
model = Completions("pollinations::evil", ctx, bot, guild_id)

# Text generation
response = await model.completion([
    {"role": "user", "content": "Hello, how are you?"}
])

# Image generation
image_url = await model._generate_image("a beautiful sunset")
```

**Supported Models**:

- `pollinations::evil` - Uncensored text model
- `pollinations::flux` - Image generation
- `pollinations::sdxl` - Stable Diffusion XL

## 🛠️ Tools

### Base Tool Interface

**Location**: `core/types.py`

All tools implement this interface:

```python
class Tool:
    def __init__(self, method_send, discord_ctx, discord_bot):
        self._method_send = method_send
        self._discord_ctx = discord_ctx
        self._discord_bot = discord_bot
    
    async def execute(self, function_name: str, **kwargs):
        """Execute tool function"""
        if hasattr(self, function_name):
            return await getattr(self, function_name)(**kwargs)
        else:
            raise ValueError(f"Function {function_name} not found")
```

### Memory Tool

**Location**: `tools/Memory/tool.py`

```python
from tools.Memory.tool import Memory

# Initialize
memory = Memory(method_send, ctx, bot)

# Store information
await memory.store_memory(
    user_id="123456789",
    content="User likes pizza",
    category="preferences"
)

# Retrieve information
memories = await memory.search_memories(
    user_id="123456789",
    query="pizza",
    limit=5
)

# Delete memory
await memory.delete_memory(memory_id="memory_123")
```

**Functions**:

- `store_memory(user_id, content, category)` - Store new memory
- `search_memories(user_id, query, limit)` - Search memories
- `delete_memory(memory_id)` - Delete specific memory
- `get_memory_stats(user_id)` - Get memory statistics

### CryptoPrice Tool

**Location**: `tools/CryptoPrice/tool.py`

```python
from tools.CryptoPrice.tool import CryptoPrice

# Initialize
crypto = CryptoPrice(method_send, ctx, bot)

# Get token price
price = await crypto.get_token_price("SOL")
print(f"Solana price: ${price}")

# Get multiple prices
prices = await crypto.get_multiple_prices(["SOL", "ETH", "BONK"])
```

**Functions**:

- `get_token_price(symbol)` - Get single token price
- `get_multiple_prices(symbols)` - Get multiple token prices
- `get_token_info(symbol)` - Get detailed token information

## 🗄️ Database

### Collections

**Chat History**

```javascript
{
  "_id": ObjectId,
  "guild_id": "123456789",
  "user_id": "987654321",
  "message_id": "111222333",
  "content": "User message content",
  "response": "Bot response content",
  "model": "openai::gpt-4",
  "timestamp": ISODate("2024-01-01T00:00:00Z"),
  "tools_used": ["Memory", "CryptoPrice"]
}
```

**Memories**

```javascript
{
  "_id": ObjectId,
  "user_id": "987654321",
  "guild_id": "123456789",
  "content": "Memory content",
  "category": "preferences",
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "last_accessed": ISODate("2024-01-01T00:00:00Z"),
  "access_count": 5,
  "embedding": [0.1, 0.2, 0.3, ...]  // Vector embedding
}
```

**Guild Settings**

```javascript
{
  "_id": ObjectId,
  "guild_id": "123456789",
  "default_model": "pollinations::evil",
  "default_tool": "Memory",
  "auto_image_enabled": true,
  "engagement_enabled": false,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Indexes

```python
# Create indexes for optimal performance
await collection.create_index("guild_id")
await collection.create_index("user_id")
await collection.create_index([("guild_id", 1), ("user_id", 1)])
await collection.create_index([("created_at", -1)])
await collection.create_index([("content", "text")])  # Text search
```

## ⚡ Caching

### Cache Configuration

```python
# Cache instances with different TTLs
api_cache = LRUCache(max_size=500, default_ttl=300)    # 5 minutes
db_cache = LRUCache(max_size=200, default_ttl=600)     # 10 minutes
model_cache = LRUCache(max_size=50, default_ttl=1800)  # 30 minutes
```

### Cache Decorator

```python
from core.services.cache_manager import cached

# Cache function results
@cached(ttl=300, cache_instance=api_cache)
async def expensive_api_call(parameter: str):
    # This result will be cached for 5 minutes
    return await external_api_call(parameter)

# Cache with custom key
@cached(ttl=600, cache_instance=db_cache)
async def database_query(user_id: str, query: str):
    # This result will be cached for 10 minutes
    return await db.find_one("users", {"user_id": user_id})
```

### Cache Management

```python
# Clear specific caches
from core.services.cache_manager import clear_api_cache, clear_db_cache, clear_all_caches

clear_api_cache()    # Clear API response cache
clear_db_cache()     # Clear database query cache
clear_all_caches()   # Clear all caches

# Get cache statistics
from core.services.cache_manager import cache_stats, CacheMonitor

stats = cache_stats()
report = CacheMonitor.get_performance_report()
```

## 📊 Performance Monitoring

### Performance Metrics

```python
from core.services.performance_monitor import get_performance_summary

summary = get_performance_summary()

# System metrics
system = summary.get("system", {})
cpu_percent = system.get("current_cpu_percent", 0)
memory_percent = system.get("current_memory_percent", 0)
memory_used_gb = system.get("current_memory_used_gb", 0)
uptime = system.get("uptime_formatted", "Unknown")

# Command metrics
commands = summary.get("commands", {})
total_commands = commands.get("total_commands", 0)
avg_response_time = commands.get("avg_response_time", 0)
commands_per_minute = commands.get("commands_per_minute", 0)

# API metrics
api = summary.get("api", {})
total_requests = api.get("total_requests", 0)
success_rate = api.get("success_rate", 0)
avg_response_time = api.get("avg_response_time", 0)
```

### Custom Metrics

```python
from core.services.performance_monitor import PerformanceMonitor

# Track custom metrics
monitor = PerformanceMonitor()

# Track function execution time
@monitor.track_function("custom_function")
async def custom_function():
    # Function implementation
    pass

# Track API calls
@monitor.track_api("external_api")
async def external_api_call():
    # API call implementation
    pass

# Track database operations
@monitor.track_database("user_query")
async def user_query():
    # Database operation
    pass
```

## ❌ Error Handling

### Custom Exceptions

**Location**: `core/exceptions/__init__.py`

```python
from core.exceptions import (
    CustomErrorMessage,
    ModelAPIKeyUnset,
    DatabaseConnectionError,
    RateLimitExceeded,
    InvalidInputError
)

# Usage
try:
    result = await some_operation()
except CustomErrorMessage as e:
    await ctx.respond(f"❌ {e}")
except ModelAPIKeyUnset:
    await ctx.respond("❌ API key not configured")
except RateLimitExceeded:
    await ctx.respond("❌ Rate limit exceeded, please wait")
```

### Exception Types

- `CustomErrorMessage` - User-friendly error messages
- `ModelAPIKeyUnset` - Missing API key for AI model
- `DatabaseConnectionError` - Database connection issues
- `RateLimitExceeded` - API rate limit exceeded
- `InvalidInputError` - Invalid user input
- `ToolNotAvailable` - Requested tool not available

### Error Handling Patterns

```python
# Command error handling
async def safe_command(self, ctx, parameter: str):
    try:
        # Validate input
        if not parameter or len(parameter) > 1000:
            raise InvalidInputError("Parameter too long or empty")
        
        # Execute operation
        result = await expensive_operation(parameter)
        
        # Return success
        await ctx.respond(f"✅ {result}")
        
    except InvalidInputError as e:
        await ctx.respond(f"❌ Invalid input: {e}", ephemeral=True)
    except CustomErrorMessage as e:
        await ctx.respond(f"❌ {e}", ephemeral=True)
    except Exception as e:
        logging.error(f"Unexpected error in safe_command: {e}")
        await ctx.respond("❌ An unexpected error occurred", ephemeral=True)
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
DISCORD_TOKEN=your_discord_token
MONGODB_URI=mongodb://localhost:27017/jakeybot

# AI Provider API Keys (only POLLINATIONS_API_KEY is required for current models)
POLLINATIONS_API_KEY=your_pollinations_key

# Optional API Keys for additional models
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
AZURE_AI_API_KEY=your_azure_key
XAI_API_KEY=your_grok_key
OPENROUTER_API_KEY=your_openrouter_key

# Optional
BOT_PREFIX=!
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_CACHE_MONITORING=true
LOG_LEVEL=INFO
```

### Configuration Validation

```python
from core.services.config_validator import validate_configuration, get_config_summary

# Validate configuration
validate_configuration()

# Get configuration summary
summary = get_config_summary()
print(f"Bot: {summary['bot_name']}")
print(f"AI Providers: {len(summary['ai_providers_configured'])}")
print(f"Database: {'Configured' if summary['database_configured'] else 'Not configured'}")
```

## 📚 Examples

### Complete Command Example

```python
import discord
from discord.ext import commands
from core.services.cache_manager import cached, api_cache
from core.exceptions import CustomErrorMessage, InvalidInputError

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(
        name="example",
        description="Example command with full error handling"
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def example_command(self, ctx, parameter: str):
        """Example command with comprehensive error handling and caching"""
        try:
            # Validate input
            if not parameter or len(parameter) > 1000:
                raise InvalidInputError("Parameter must be between 1 and 1000 characters")
            
            # Get cached result or compute new
            result = await self._get_cached_result(parameter)
            
            # Send response
            await ctx.respond(f"✅ Result: {result}")
            
        except InvalidInputError as e:
            await ctx.respond(f"❌ Invalid input: {e}", ephemeral=True)
        except CustomErrorMessage as e:
            await ctx.respond(f"❌ {e}", ephemeral=True)
        except Exception as e:
            logging.error(f"Unexpected error in example_command: {e}")
            await ctx.respond("❌ An unexpected error occurred", ephemeral=True)
    
    @cached(ttl=300, cache_instance=api_cache)
    async def _get_cached_result(self, parameter: str):
        """Cached expensive operation"""
        # Simulate expensive operation
        await asyncio.sleep(1)
        return f"Processed: {parameter}"

def setup(bot):
    bot.add_cog(ExampleCog(bot))
```

### Tool Integration Example

```python
from tools.Memory.tool import Memory
from tools.CryptoPrice.tool import CryptoPrice

class IntegratedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="smart_query")
    async def smart_query(self, ctx, query: str):
        """Smart query using multiple tools"""
        try:
            # Initialize tools
            memory = Memory(self._method_send, ctx, self.bot)
            crypto = CryptoPrice(self._method_send, ctx, self.bot)
            
            # Check memory for previous interactions
            memories = await memory.search_memories(
                user_id=str(ctx.author.id),
                query=query,
                limit=3
            )
            
            # If query mentions crypto, get prices
            if any(word in query.lower() for word in ['bitcoin', 'eth', 'sol', 'crypto']):
                prices = await crypto.get_multiple_prices(['BTC', 'ETH', 'SOL'])
                price_info = f"Current prices: BTC=${prices['BTC']}, ETH=${prices['ETH']}, SOL=${prices['SOL']}"
            else:
                price_info = ""
            
            # Store interaction in memory
            await memory.store_memory(
                user_id=str(ctx.author.id),
                content=f"User asked: {query}",
                category="queries"
            )
            
            # Send response
            response = f"Query: {query}\n"
            if memories:
                response += f"Related memories: {len(memories)} found\n"
            if price_info:
                response += price_info
            
            await ctx.respond(response)
            
        except Exception as e:
            await ctx.respond(f"❌ Error: {e}", ephemeral=True)
```

---

**For more information, see the [Developer Guide](./DEVELOPER_GUIDE.md) or [Contributing Guidelines](./CONTRIBUTING.md).**
