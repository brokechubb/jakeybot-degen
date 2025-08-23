# 🧠 Memory Tool Demonstration

This document demonstrates how the new Memory tool works in JakeyBot, allowing the bot to automatically remember and recall information across conversations.

## 🎯 How It Works

The Memory tool provides three main functions:

1. **`remember_fact`** - Automatically stores new information
2. **`recall_fact`** - Searches for and retrieves relevant information
3. **`list_facts`** - Lists stored information by category

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

## 📝 Example Conversations

### Example 1: Remembering User Information

**User:** "My name is Jimmy"
**Jakey:** "Nice to meet you, Jimmy! I'll remember that for our future conversations."

*Behind the scenes:* The bot automatically calls `remember_fact` with the fact "My name is Jimmy" and category "personal_info"

### Example 2: Recalling Information

**User:** "What's my name?"
**Jakey:** "Your name is Jimmy! I remembered that from our previous conversation."

*Behind the scenes:* The bot calls `recall_fact` with query "name" and finds the stored information

### Example 3: Remembering Preferences

**User:** "I love pizza and my favorite color is blue"
**Jakey:** "Great choices! I'll remember that you love pizza and your favorite color is blue."

*Behind the scenes:* The bot stores multiple facts about your preferences

### Example 4: Future Conversation Recall

**User (in a new conversation):** "What do you know about me?"
**Jakey:** "Based on what I remember: Your name is Jimmy, you love pizza, and your favorite color is blue!"

### Example 5: Memory Debugging

**User:** "Why isn't the memory working?"
**Jakey:** "Let me check the memory system status for you..."

**User:** /memory_debug
**Jakey:** "🧠 Memory System Status:
❌ Database connection: Failed
📊 Total facts stored: 0
🔍 Search index: Unavailable
⚠️ Issue: MongoDB connection timeout"

### Example 6: Memory Reindexing

**User:** "I can't find the information I shared earlier"
**Jakey:** "Let me reindex the memory system to fix the search issues..."

**User:** /memory_reindex
**Jakey:** "🔄 Memory system reindexing... This may take a moment.
✅ Reindexing complete! Try asking about your information again."

## 🔧 Technical Implementation

### Automatic Memory Detection

The bot automatically detects when users share personal information by:

1. **Pattern Recognition** - Identifying statements like "My name is...", "I like...", "My favorite...", etc.
2. **Context Analysis** - Understanding when information is being shared vs. requested
3. **Relevance Scoring** - Determining what information is worth remembering

### Memory Storage

- **Structured Storage** - Facts are stored with categories, timestamps, and expiration dates
- **User Association** - Each fact is linked to the user who shared it
- **Guild Isolation** - Facts are separated by Discord server (unless shared history is enabled)
- **Enhanced Database** - Shared database connection across all bot components for better performance

### Smart Recall

- **Semantic Search** - The bot searches memory using natural language queries
- **Relevance Ranking** - Most relevant facts are returned first
- **Context Integration** - Retrieved facts are seamlessly integrated into responses
- **Search Optimization** - Automatic indexing and reindexing for optimal performance

## 🚀 Usage Examples

### For Users

Simply share information naturally in conversation:

- "I'm a software developer"
- "My birthday is March 15th"
- "I enjoy hiking and photography"
- "I have a dog named Max"

### Memory Management

Use the new commands to manage and troubleshoot memory:

- **`/memory_debug`** - Check system status
- **`/memory_reindex`** - Fix search issues
- **`/feature Memory`** - Enable memory tool

### For Bot Administrators

The Memory tool can be enabled via:

1. **Environment Variable:** Set `DEFAULT_TOOL=Memory` in your `.env` file
2. **Slash Command:** Use `/feature Memory` to enable it for a specific guild
3. **Automatic Integration:** The tool works seamlessly with existing AI models
4. **Management Scripts:** Use `python scripts/setup_memory.py` for server-wide setup

## 📊 Memory Categories

The bot automatically categorizes information:

- **`[personal_info]`** - Names, birthdays, locations
- **`[preferences]`** - Likes, dislikes, favorites
- **`[interests]** - Hobbies, activities, skills
- **`[relationships]`** - Family, friends, pets
- **`[custom]`** - User-defined categories

## ⚙️ Configuration Options

### Expiration Times

- **Temporary:** "1h", "2d", "30m" (automatically expires)
- **Permanent:** "never" (stored indefinitely)
- **Default:** No expiration (stored permanently)

### Search Limits

- **Max Results:** 10 facts per search
- **Search Depth:** Full database scan
- **Performance:** Optimized with automatic indexing

### Database Options

- **Shared Connection:** All bot components use the same database connection
- **Automatic Backup:** Regular backups to prevent data loss
- **Health Monitoring:** Built-in health checks and status reporting

## 🆘 Troubleshooting

### Common Issues

**Memory not working:**
1. Check if Memory tool is enabled: `/feature Memory`
2. Debug system status: `/memory_debug`
3. Check database connection
4. Contact server administrator

**Search not finding information:**
1. Try `/memory_reindex` to rebuild search index
2. Check if information was actually stored
3. Verify search query matches stored facts
4. Use `/memory_debug` to check system health

**Database connection issues:**
1. Run `/memory_debug` to see connection status
2. Check MongoDB configuration
3. Verify network connectivity
4. Contact server administrator

### Getting Help

- **Use `/memory_debug`** for system status
- **Try `/memory_reindex`** for search issues
- **Check tool status** with `/feature`
- **Contact server admins** for persistent issues

---

**🧠 The Memory tool makes JakeyBot truly personal by remembering your preferences and information across conversations. Use the new debugging commands to keep it running smoothly!**
