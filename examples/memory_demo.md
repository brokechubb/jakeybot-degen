# 🧠 Memory Tool Demonstration

This document demonstrates how the new Memory tool works in JakeyBot, allowing the bot to automatically remember and recall information across conversations.

## 🎯 How It Works

The Memory tool provides three main functions:

1. **`remember_fact`** - Automatically stores new information
2. **`recall_fact`** - Searches for and retrieves relevant information
3. **`list_facts`** - Lists stored information by category

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

### Smart Recall

- **Semantic Search** - The bot searches memory using natural language queries
- **Relevance Ranking** - Most relevant facts are returned first
- **Context Integration** - Retrieved facts are seamlessly integrated into responses

## 🚀 Usage Examples

### For Users

Simply share information naturally in conversation:

- "I'm a software developer"
- "My birthday is March 15th"
- "I enjoy hiking and photography"
- "I have a dog named Max"

### For Bot Administrators

The Memory tool can be enabled via:

1. **Environment Variable:** Set `DEFAULT_TOOL=Memory` in your `.env` file
2. **Slash Command:** Use `/feature Memory` to enable it for a specific guild
3. **Automatic Integration:** The tool works seamlessly with existing AI models

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

- **Default Recall:** 3 facts per search
- **Maximum Recall:** 10 facts per search
- **List Facts:** Up to 20 facts per category

## 🔒 Privacy & Security

- **User Isolation** - Facts are only accessible to the user who shared them
- **Guild Separation** - Facts are isolated by Discord server
- **Expiration Control** - Users can set how long information is stored
- **Manual Deletion** - Users can remove stored information if needed

## 🎉 Benefits

1. **Personalized Experience** - The bot remembers your preferences and details
2. **Contextual Responses** - Answers are tailored to your specific situation
3. **Long-term Memory** - Information persists across conversations and sessions
4. **Natural Interaction** - No need to manually input information repeatedly
5. **Privacy Respect** - Information is stored securely and isolated by user/guild

## 🚧 Limitations

- **Model Dependency** - Requires AI models that support tool calling
- **Storage Limits** - Facts are stored in MongoDB with potential size constraints
- **Search Accuracy** - Depends on the quality of the semantic search implementation
- **Expiration Management** - Expired facts are automatically cleaned up but may persist in search results temporarily

## 🔮 Future Enhancements

Potential improvements for the Memory tool:

- **Advanced Categorization** - AI-powered automatic categorization
- **Memory Consolidation** - Merging related facts and removing duplicates
- **Memory Analytics** - Insights into what information is most/least useful
- **Export/Import** - Ability to backup and restore memory data
- **Memory Sharing** - Option to share certain facts with other users
- **Memory Visualization** - Dashboard showing stored information and relationships
