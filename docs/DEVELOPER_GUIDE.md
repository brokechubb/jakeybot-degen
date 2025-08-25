# 🛠️ JakeyBot Developer Guide

Comprehensive guide for developers working on JakeyBot, including architecture, development practices, and contribution guidelines.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Code Structure](#code-structure)
4. [Adding New Features](#adding-new-features)
5. [Testing Guidelines](#testing-guidelines)
6. [Performance Optimization](#performance-optimization)
7. [Security Best Practices](#security-best-practices)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

### Core Components

JakeyBot follows a modular architecture with clear separation of concerns:

```
JakeyBot/
├── main.py                 # Bot entry point and initialization
├── core/                   # Core services and utilities
│   ├── ai/                # AI integration layer
│   ├── services/          # Service layer (cache, database, etc.)
│   ├── exceptions/        # Custom exception classes
│   └── types.py           # Type definitions
├── cogs/                  # Discord command modules
│   ├── ai/               # AI-related commands
│   ├── admin.py          # Administrative commands
│   └── misc.py           # Miscellaneous utilities
├── aimodels/             # AI provider integrations
│   ├── openai/           # OpenAI integration
│   ├── gemini/           # Google Gemini integration
│   ├── claude/           # Anthropic Claude integration
│   └── pollinations/     # Pollinations.AI integration
├── tools/                # External service integrations
│   ├── Memory/           # Memory management
│   ├── CryptoPrice/      # Cryptocurrency price data
│   └── YouTube/          # YouTube analysis
└── data/                 # Configuration files
    ├── models.yaml       # AI model definitions
    ├── assistants.yaml   # Assistant configurations
    └── prompts/          # Prompt templates
```

### Design Patterns

- **Service Layer Pattern**: Core services handle business logic
- **Repository Pattern**: Database operations abstracted through managers
- **Factory Pattern**: AI model instantiation
- **Observer Pattern**: Event-driven architecture for Discord events
- **Decorator Pattern**: Caching and performance monitoring

## 🚀 Development Setup

### Prerequisites

- Python 3.11+ (recommended)
- Git
- MongoDB (for production)
- Discord Bot Token
- API Keys for AI providers

### Local Development

```bash
# Clone the repository
git clone https://github.com/brokechubb/JakeyBot.git
cd JakeyBot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp dev.env.template dev.env

# Edit dev.env with your API keys
nano dev.env

# Run security check
python scripts/security_check.py

# Start the bot
python main.py
```

### Environment Variables

Required environment variables in `dev.env`:

```bash
# Bot Configuration
DISCORD_TOKEN=your_discord_token
BOT_PREFIX=!

# Database
MONGODB_URI=mongodb://localhost:27017/jakeybot

# AI Provider API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
AZURE_AI_API_KEY=your_azure_key
XAI_API_KEY=your_grok_key
OPENROUTER_API_KEY=your_openrouter_key
POLLINATIONS_API_KEY=your_pollinations_key

# Optional: Performance Monitoring
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_CACHE_MONITORING=true
```

## 📁 Code Structure

### Adding New Commands

Commands are organized in the `cogs/` directory. Each cog represents a functional area:

```python
# cogs/example.py
import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(
        name="example",
        description="Example command"
    )
    async def example_command(self, ctx, parameter: str):
        """Command documentation"""
        await ctx.respond(f"Example response: {parameter}")

def setup(bot):
    bot.add_cog(ExampleCog(bot))
```

### Adding New AI Models

AI models are implemented in the `aimodels/` directory:

```python
# aimodels/example/infer.py
from .config import ModelParams
from core.exceptions import CustomErrorMessage

class Completions(ModelParams):
    def __init__(self, model_name, discord_ctx, discord_bot, guild_id=None):
        super().__init__()
        self._model_name = model_name
        self._discord_ctx = discord_ctx
        self._discord_bot = discord_bot
        self._guild_id = guild_id
    
    async def completion(self, conversation, return_text=True):
        """Main completion method"""
        try:
            # Implementation here
            return response
        except Exception as e:
            raise CustomErrorMessage(f"Error: {e}")
```

### Adding New Tools

Tools are implemented in the `tools/` directory:

```python
# tools/ExampleTool/tool.py
from core.types import Tool

class ExampleTool(Tool):
    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__(method_send, discord_ctx, discord_bot)
    
    async def example_function(self, parameter: str) -> str:
        """Tool function implementation"""
        # Implementation here
        return result
```

## 🔧 Adding New Features

### 1. Command Development

**Best Practices:**

- Use slash commands for user-facing functionality
- Implement proper error handling
- Add comprehensive help text
- Use ephemeral responses for sensitive operations
- Implement rate limiting for expensive operations

**Example:**

```python
@commands.slash_command(
    name="new_feature",
    description="Description of the new feature"
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def new_feature(self, ctx, parameter: str):
    """Detailed command documentation"""
    try:
        # Implementation
        await ctx.respond("Success!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Error: {e}", ephemeral=True)
```

### 2. AI Integration

**Steps:**

1. Create model configuration in `data/models.yaml`
2. Implement model class in `aimodels/provider/`
3. Add error handling and fallbacks
4. Test with various inputs
5. Update documentation

### 3. Database Operations

**Pattern:**

```python
from core.services.database_manager import DatabaseManager

class ExampleManager(DatabaseManager):
    async def create_example(self, guild_id: str, data: dict):
        """Create new example record"""
        return await self._collection.insert_one({
            "guild_id": guild_id,
            "data": data,
            "created_at": datetime.utcnow()
        })
    
    async def get_example(self, guild_id: str):
        """Get example by guild ID"""
        return await self._collection.find_one({"guild_id": guild_id})
```

## 🧪 Testing Guidelines

### Unit Testing

```python
# tests/test_example.py
import pytest
from unittest.mock import Mock, patch
from cogs.example import ExampleCog

class TestExampleCog:
    @pytest.fixture
    def cog(self):
        bot = Mock()
        return ExampleCog(bot)
    
    @pytest.mark.asyncio
    async def test_example_command(self, cog):
        ctx = Mock()
        ctx.respond = Mock()
        
        await cog.example_command(ctx, "test")
        
        ctx.respond.assert_called_once_with("Example response: test")
```

### Integration Testing

```python
# tests/integration/test_ai_integration.py
import pytest
from aimodels.openai.infer import Completions

@pytest.mark.asyncio
async def test_openai_completion():
    # Test AI model integration
    model = Completions("openai::gpt-4", None, None)
    response = await model.completion(["Hello"])
    assert response is not None
```

### Performance Testing

```python
# tests/performance/test_cache.py
import time
from core.services.cache_manager import api_cache

def test_cache_performance():
    start_time = time.time()
    
    # Test cache operations
    api_cache.set("test_key", "test_value")
    value = api_cache.get("test_key")
    
    end_time = time.time()
    assert end_time - start_time < 0.1  # Should be fast
    assert value == "test_value"
```

## ⚡ Performance Optimization

### Caching Strategy

```python
from core.services.cache_manager import cached, api_cache

@cached(ttl=300, cache_instance=api_cache)
async def expensive_api_call(parameter: str):
    """Expensive API call with 5-minute cache"""
    # Implementation
    return result
```

### Database Optimization

```python
# Create indexes for frequently queried fields
await collection.create_index("guild_id")
await collection.create_index("user_id")
await collection.create_index([("created_at", -1)])
```

### Memory Management

```python
# Use generators for large datasets
async def stream_large_dataset():
    async for document in collection.find():
        yield document

# Batch operations
async def batch_insert(documents):
    await collection.insert_many(documents)
```

## 🔒 Security Best Practices

### API Key Management

```python
# Never hardcode API keys
api_key = environ.get("API_KEY")
if not api_key:
    raise CustomErrorMessage("API key not configured")

# Validate API keys
def validate_api_key(key: str) -> bool:
    return bool(key and len(key) > 10)
```

### Input Validation

```python
from core.services.input_validator import validate_input

async def safe_command(self, ctx, user_input: str):
    # Validate input
    if not validate_input(user_input, max_length=1000):
        await ctx.respond("Invalid input", ephemeral=True)
        return
    
    # Process validated input
    result = await process_input(user_input)
```

### Rate Limiting

```python
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 per minute per user
@commands.cooldown(5, 300, commands.BucketType.guild)  # 5 per 5 minutes per guild
async def rate_limited_command(self, ctx):
    # Implementation
    pass
```

## 🚀 Deployment

### Production Setup

```bash
# Install production dependencies
pip install -r requirements.txt

# Set up MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Configure firewall
sudo ufw allow 27017  # MongoDB
sudo ufw allow 22     # SSH

# Set up systemd service
sudo nano /etc/systemd/system/jakeybot.service
```

### Systemd Service

```ini
[Unit]
Description=JakeyBot Discord Bot
After=network.target

[Service]
Type=simple
User=jakeybot
WorkingDirectory=/opt/jakeybot
Environment=PATH=/opt/jakeybot/venv/bin
ExecStart=/opt/jakeybot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**2. Database Connection Issues**

```python
# Test database connection
from core.services.database_manager import DatabaseManager
db = DatabaseManager()
await db.test_connection()
```

**3. API Key Issues**

```python
# Validate API keys
from core.services.config_validator import validate_configuration
validate_configuration()
```

**4. Performance Issues**

```python
# Check cache performance
from core.services.cache_manager import cache_stats
stats = cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable performance monitoring
environ["ENABLE_PERFORMANCE_MONITORING"] = "true"
```

### Log Analysis

```bash
# View recent logs
tail -f logs/jakeybot.log

# Search for errors
grep "ERROR" logs/jakeybot.log

# Monitor performance
grep "PERFORMANCE" logs/jakeybot.log
```

## 📚 Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)
- [JakeyBot API Documentation](./API.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

For detailed contribution guidelines, see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

**Need Help?** Open an issue on GitHub or join our Discord server for support.
