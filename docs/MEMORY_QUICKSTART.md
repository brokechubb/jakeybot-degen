# 🧠 Memory Tool Quick Start Guide

Get up and running with JakeyBot's Memory tool in just a few minutes!

## 🚀 Quick Setup

### 1. Enable the Memory Tool

**Option A: Set as Default (Recommended)**

```bash
# Run the setup script
python scripts/setup_memory.py
```

**Option B: Manual Configuration**

```bash
# Edit your .env file
DEFAULT_TOOL=Memory
```

**Option C: Per-Guild Enable**

```
/feature Memory
```

### 2. Restart Your Bot

After enabling the Memory tool, restart JakeyBot for the changes to take effect.

## 🧪 Test the Memory System

### Basic Test

1. **Share Information:**

   ```
   My name is Jimmy
   ```

2. **Bot Response:**

   ```
   Nice to meet you, Jimmy! I'll remember that for our future conversations.
   ```

3. **Ask for Recall:**

   ```
   What's my name?
   ```

4. **Bot Response:**

   ```
   Your name is Jimmy! I remembered that from our previous conversation.
   ```

### Advanced Test

1. **Share Multiple Facts:**

   ```
   I love pizza, my favorite color is blue, and I'm a software developer
   ```

2. **Ask Complex Questions:**

   ```
   What do you know about me?
   ```

3. **Bot Response:**

   ```
   Based on what I remember: Your name is Jimmy, you love pizza, your favorite color is blue, and you're a software developer!
   ```

## 📝 What Gets Remembered

### ✅ **DO Remember:**

- Names and personal details
- Preferences and favorites
- Interests and hobbies
- Important dates
- Skills and expertise
- Relationships and pets

### ❌ **DON'T Remember:**

- Temporary requests
- Commands and instructions
- Non-personal information
- Sensitive data
- Temporary preferences

### 🔍 **Username Association**

**Important**: All stored facts are automatically prefixed with the username who shared them in the format `[Username] fact_text`.

**Benefits:**
- **Clear Attribution**: You can see exactly who shared what information
- **No Confusion**: Multiple users can share similar information without conflicts
- **Personal Context**: Names and preferences are clearly linked to specific users
- **Better Recall**: The bot can distinguish between different users' information

**Examples:**
```
[Jimmy] my name is Jimmy
[Jimmy] I like pizza
[Sarah] my name is Sarah  
[Sarah] I love hiking
```

This prevents confusion when multiple users have similar names or preferences!

## 🔧 Manual Commands

### Store Information Manually

```
/remember I love hiking and photography
```

### Set Expiration Times

```
/remember My vacation ends next Friday expires_in:1w
```

**Expiration Formats:**

- `1d` = 1 day
- `2h` = 2 hours
- `30m` = 30 minutes
- `1w` = 1 week
- `never` = permanent

## 🆕 New Memory Management Commands

### Memory Debugging

**`/memory_debug`** - Check memory system status and troubleshoot issues:

```
User: /memory_debug
Jakey: 🧠 Memory System Status:
✅ Database connection: Active
📊 Total facts stored: 47
🔍 Search index: Healthy
⏰ Last backup: 2 hours ago
```

**Use when:**
- Memory isn't working properly
- Want to check system health
- Troubleshooting issues
- Monitoring system status

### Memory Reindexing

**`/memory_reindex`** - Fix search problems by rebuilding the search index:

```
User: /memory_reindex
Jakey: 🔄 Memory system reindexing... This may take a moment.
✅ Reindexing complete! Search should now work properly.
```

**Use when:**
- Search isn't finding stored information
- Memory recall is inconsistent
- After database changes
- Improving search accuracy

## 🎯 Pro Tips

### 1. **Natural Conversation**

Just share information naturally - the bot will automatically detect and remember it!

### 2. **Category Organization**

The bot automatically categorizes information:

- `[personal_info]` - Names, details
- `[preferences]` - Likes, favorites
- `[interests]` - Hobbies, skills
- `[relationships]` - Family, friends

### 3. **Context Matters**

The bot is smart about context:

- "I like pizza" → Gets remembered
- "Can you get me pizza?" → Not remembered (it's a request)

### 4. **Memory Persistence**

- Information persists across conversations
- Works even after bot restarts
- Respects Discord server boundaries
- User-specific privacy

## 🛠️ Management & Monitoring

### Check Tool Status

```bash
# View all tools status
python scripts/manage_tools.py

# Check Memory tool specifically
python scripts/manage_tools.py status Memory
```

### Set as Default Tool

```bash
# Set Memory as default for new users
python scripts/setup_memory.py

# Set for existing users
python scripts/set_default_tool.py Memory
```

### Test Tool Functionality

```bash
# Run comprehensive tests
python scripts/test_memory.py

# Test memory fixes and improvements
python scripts/test_memory_fix.py
```

## 🚨 Troubleshooting

### Memory Not Working?

1. **Check Tool Status:**

   ```
   /feature
   ```

   Look for "Memory" in the enabled tools.

2. **Debug Memory System:**

   ```
   /memory_debug
   ```

   This will show you the current system status and any issues.

3. **Verify Configuration:**

   ```bash
   python scripts/setup_memory.py
   ```

4. **Check Database:**
   Ensure MongoDB is running and accessible.

5. **Model Compatibility:**
   Memory tool requires AI models that support tool calling.

6. **Use Management Scripts:**

   ```bash
   # Check tool health
   python scripts/manage_tools.py status Memory
   
   # View database statistics
   python scripts/manage_tools.py
   ```

### Common Issues

- **"Tool not available"** → Enable Memory tool with `/feature Memory`
- **"Database connection failed"** → Check MongoDB connection string
- **"No facts found"** → Try sharing some information first
- **"Memory not working"** → Restart bot after configuration changes
- **"Search not working"** → Try `/memory_reindex` to fix search issues

### Advanced Troubleshooting

**Search Issues:**
1. Use `/memory_debug` to check system status
2. Try `/memory_reindex` to rebuild search index
3. Check if information was actually stored
4. Verify search query matches stored facts

**Database Issues:**
1. Run `/memory_debug` to see connection status
2. Check MongoDB configuration
3. Verify network connectivity
4. Contact server administrator

## 📚 Advanced Usage

### Custom Categories

The bot automatically detects categories, but you can be explicit:

```
My name is Jimmy [personal_info]
I love pizza [preferences]
I'm a developer [interests]
```

### Memory Management

- Facts are automatically cleaned up when expired
- You can manually delete information if needed
- Memory is isolated by user and Discord server
- Enhanced database connection for better performance

### Integration with Other Tools

Memory works seamlessly with:

- All AI models that support tool calling
- Existing knowledge base commands
- Chat history and context systems
- New reminder system and time commands

## 🎉 You're Ready

The Memory tool is now active and will automatically:

- Remember personal information you share
- Recall relevant details when you ask questions
- Provide personalized responses based on your preferences
- Maintain privacy and data isolation
- Provide debugging tools for troubleshooting

Start sharing information naturally and watch JakeyBot remember and recall it in future conversations!

## 📖 Need Help?

- **Documentation:** Check `docs/MEMORY_IMPLEMENTATION.md`
- **Examples:** See `examples/memory_demo.md`
- **Issues:** Check the troubleshooting section above
- **Management Scripts:** Use the provided scripts for advanced management
- **Support:** Join the JakeyBot community for help
- **Debugging:** Use `/memory_debug` and `/memory_reindex` commands

## 🔍 Quick Commands Reference

```bash
# Setup and Configuration
python scripts/setup_memory.py          # Set up Memory tool
python scripts/test_memory.py           # Test functionality
python scripts/test_memory_fix.py       # Test memory fixes
python scripts/manage_tools.py          # View tool status

# Management
python scripts/set_default_tool.py Memory  # Set as default
python scripts/manage_tools.py status Memory  # Check health
```

**Discord Commands:**
- `/memory_debug` - Check memory system status
- `/memory_reindex` - Fix search issues
- `/feature Memory` - Enable memory tool
- `/remember <fact>` - Manually store information
