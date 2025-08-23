# 🧠 Memory Tool Implementation

This document details the technical implementation of the Memory tool for JakeyBot, which enables automatic memory recall across conversations.

## 🏗️ Architecture Overview

The Memory tool is implemented as a standard tool following JakeyBot's tool architecture pattern:

```
tools/Memory/
├── __init__.py          # Package initialization
├── manifest.py          # Tool schema and metadata
└── tool.py             # Core tool implementation
```

## 🔧 Core Components

### 1. Tool Manifest (`manifest.py`)

Defines the tool schema for three main functions:

- **`remember_fact`** - Stores new information with optional categorization and expiration
- **`recall_fact`** - Searches for relevant information using semantic queries
- **`list_facts`** - Lists stored information by category

### 2. Tool Implementation (`tool.py`)

Implements the actual functionality:

- **Database Integration** - Connects to MongoDB via the existing History class
- **User Context** - Determines guild/user IDs for proper data isolation
- **Expiration Handling** - Parses and manages fact expiration times
- **Error Handling** - Graceful fallbacks when database operations fail

### 3. System Integration

The Memory tool integrates with JakeyBot's existing systems:

- **History Database** - Uses the existing knowledge base infrastructure
- **AI Models** - Works with all models that support tool calling
- **User Management** - Respects guild/user isolation settings
- **Configuration** - Can be set as default tool via environment variables

## 🔄 Data Flow

### Memory Storage Flow

1. **User Input** → Bot detects personal information sharing
2. **AI Analysis** → Determines what should be remembered
3. **Tool Call** → `remember_fact` function is invoked
4. **Database Storage** → Fact is stored in MongoDB with metadata
5. **User Feedback** → Bot acknowledges what was remembered

### Memory Recall Flow

1. **User Question** → Bot receives a query
2. **Memory Search** → `recall_fact` searches the knowledge base
3. **Relevance Scoring** → Facts are ranked by relevance
4. **Response Generation** → Retrieved facts are integrated into AI response
5. **Natural Output** → Bot provides personalized answer

## 🗄️ Database Schema

### Knowledge Collections

Each guild gets its own knowledge collection: `knowledge_{guild_id}`

```json
{
  "_id": "ObjectId",
  "user_id": 123456789,
  "fact_text": "[personal_info] [Username] My name is Jimmy",
  "source": "memory_tool/123456789",
  "created_at": "2024-01-01T00:00:00Z",
  "last_accessed_at": "2024-01-01T00:00:00Z",
  "relevance_score": 0,
  "expires_at": null
}
```

### Key Features

- **Username Prefixing** - All facts are prefixed with `[Username]` to clearly associate information with specific users
- **Categorization** - Facts are prefixed with category tags `[category]` after the username
- **Expiration** - Optional TTL for temporary information
- **Access Tracking** - Last accessed timestamp for analytics
- **Source Tracking** - Identifies how the fact was stored
- **User Isolation** - Each fact is linked to the user who shared it

## 🧠 AI Integration

### System Prompt Enhancement

The generative chat system now includes memory instructions:

```
IMPORTANT MEMORY INSTRUCTIONS:
1. If the user shares personal information, automatically remember it
2. When answering questions, always check memory first
3. Use memory tools to store useful facts
4. Acknowledge when remembering information
5. Present recalled information naturally
```

### Automatic Detection

The AI models are instructed to:

- **Detect Personal Information** - Names, preferences, interests, etc.
- **Store Automatically** - Use `remember_fact` without user prompting
- **Recall Contextually** - Search memory when answering questions
- **Integrate Seamlessly** - Make memory recall feel natural

## ⚙️ Configuration

### Environment Variables

```bash
# Set Memory as default tool
DEFAULT_TOOL=Memory

# MongoDB connection (required)
MONGO_DB_URL=mongodb://...
MONGO_DB_NAME=jakey_prod_db
MONGO_DB_COLLECTION_NAME=jakey_prod_db_collection

# Optional: Enable shared chat history
SHARED_CHAT_HISTORY=false
```

### Tool Selection

Users can enable the Memory tool via:

1. **Default Setting** - Set in environment variables
2. **Slash Command** - `/feature Memory`
3. **Automatic Detection** - Bot suggests it when appropriate

## 🔒 Privacy & Security

### Data Isolation

- **User Separation** - Facts are linked to specific users
- **Guild Separation** - Facts are isolated by Discord server
- **Access Control** - Only the user who shared information can access it

### Data Management

- **Expiration Control** - Users can set how long information persists
- **Manual Deletion** - Users can remove stored information
- **Audit Trail** - Source and timestamp tracking for all facts

## 🚀 Performance Considerations

### Search Optimization

- **Text Indexes** - MongoDB text search for fast fact retrieval
- **Relevance Scoring** - Simple keyword matching (can be enhanced)
- **Result Limiting** - Configurable limits to prevent overwhelming responses

### Storage Efficiency

- **Category Prefixing** - Efficient category-based queries
- **Expiration Cleanup** - Automatic removal of expired facts
- **Metadata Optimization** - Minimal overhead per stored fact

## 🧪 Testing & Validation

### Test Scripts

- **`scripts/test_memory.py`** - Unit tests for tool functionality
- **`scripts/setup_memory.py`** - Automated setup and configuration

### Test Coverage

- Tool instantiation and schema validation
- Database connection handling
- Function parameter validation
- Error handling and fallbacks

## 🛠️ Management & Monitoring

### Tool Status Monitoring

```bash
# Check overall tool health
python scripts/manage_tools.py

# View Memory tool specifically
python scripts/manage_tools.py status Memory

# Check database statistics
python scripts/manage_tools.py
```

### Configuration Management

```bash
# Set up Memory tool
python scripts/setup_memory.py

# Set as default for existing users
python scripts/set_default_tool.py Memory

# Test functionality
python scripts/test_memory.py
```

### Health Checks

The management scripts provide:

- **File integrity checks** - Verify all required files exist
- **Configuration validation** - Check environment variables
- **Database connectivity** - Test MongoDB connection
- **Tool functionality** - Basic operation testing

## 🔮 Future Enhancements

### Planned Improvements

1. **Advanced Categorization** - AI-powered automatic categorization
2. **Memory Consolidation** - Merging related facts and removing duplicates
3. **Relevance Algorithms** - Better semantic search and ranking
4. **Memory Analytics** - Insights into memory usage patterns
5. **Export/Import** - Backup and restore functionality

### Technical Debt

- **Search Algorithm** - Replace simple text matching with semantic search
- **Caching Layer** - Add Redis caching for frequently accessed facts
- **Batch Operations** - Support for bulk fact operations
- **Memory Limits** - Implement per-user/guild storage quotas

## 📚 Dependencies

### Required Packages

- **Motor** - Async MongoDB driver
- **Discord.py** - Discord bot framework
- **Core JakeyBot** - History and helper functions

### Optional Enhancements

- **Redis** - For caching and performance
- **Elasticsearch** - For advanced semantic search
- **Vector Databases** - For embedding-based similarity search

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MongoDB connection string
   - Verify network connectivity
   - Check authentication credentials

2. **Tool Not Available**
   - Ensure Memory tool is enabled via `/feature Memory`
   - Check if DEFAULT_TOOL is set correctly
   - Verify tool files are present

3. **Memory Not Working**
   - Check if AI model supports tool calling
   - Verify system prompt includes memory instructions
   - Check database permissions and indexes

### Debug Commands

```bash
# Test tool functionality
python scripts/test_memory.py

# Setup tool as default
python scripts/setup_memory.py

# Check database connection
python -c "from core.ai.history import History; print('DB OK')"

# Monitor tool status
python scripts/manage_tools.py status Memory
```

## 📖 API Reference

### Tool Functions

#### `remember_fact(fact, category=None, expires_in=None)`

Stores a new fact in memory.

**Parameters:**

- `fact` (str): The information to remember
- `category` (str, optional): Category for organization
- `expires_in` (str, optional): Expiration time (e.g., "1d", "2h", "never")

**Returns:** Success message with fact ID

#### `recall_fact(query, limit=3)`

Searches for relevant facts.

**Parameters:**

- `query` (str): Search query
- `limit` (int): Maximum results (1-10)

**Returns:** Found facts or "not found" message

#### `list_facts(category=None, limit=10)`

Lists stored facts by category.

**Parameters:**

- `category` (str, optional): Category to filter by
- `limit` (int): Maximum results (1-20)

**Returns:** List of facts or empty message

## 🎯 Conclusion

The Memory tool provides JakeyBot with persistent, intelligent memory capabilities that enhance user experience through personalized interactions. The implementation follows established patterns and integrates seamlessly with existing systems while maintaining privacy and security standards.

The tool is production-ready and can be enhanced incrementally with more advanced features as needed.

## 📚 Additional Resources

### Documentation

- **Quick Start Guide**: `docs/MEMORY_QUICKSTART.md`
- **Configuration Guide**: `docs/CONFIG.md`
- **Tools Overview**: `docs/TOOLS.md`
- **Scripts Documentation**: `scripts/README.md`

### Management Scripts

- **`scripts/manage_tools.py`** - Tool status and health monitoring
- **`scripts/setup_memory.py`** - Automated setup and configuration
- **`scripts/test_memory.py`** - Comprehensive testing suite
- **`scripts/set_default_tool.py`** - Default tool management

### Examples

- **Memory Demo**: `examples/memory_demo.md`
- **Usage Examples**: See the Quick Start Guide above
