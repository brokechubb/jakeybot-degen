# Memory and Global Facts Integration Verification

This document explains how to verify that memories and global facts are being used in JakeyBot chat responses.

## System Overview

JakeyBot integrates both user-specific memories and global facts into chat responses through a multi-layered approach:

### 1. System Prompt Integration
The `jakey_system_prompt` in `data/assistants.yaml` includes comprehensive memory instructions that guide the AI to:
- Automatically detect and remember personal information
- Proactively use stored memories in conversations
- Seamlessly integrate recalled information without showing technical details

### 2. Knowledge Base Search
The system searches for relevant facts at multiple levels:
- **User-specific memories**: Stored with `[Username]` prefixes
- **Global facts**: Stored with `[SYSTEM_GLOBAL]` prefixes in the special `knowledge_0` collection
- **Combined results**: Both types are presented to the AI for context

### 3. Real-time Fact Injection
Global facts are injected using the `/inject_fact` admin command and are immediately available across all conversations.

## How to Verify Integration is Working

### Method 1: Check System Prompt Construction
The `generative_chat.py` file now includes enhanced knowledge retrieval:

```python
# Retrieve relevant facts from knowledge base (including global facts)
facts = await self.DBConn.search_facts(guild_id, _final_prompt, limit=3)

# Also search global facts
global_facts = []
try:
    global_collection = self.DBConn._db["knowledge_0"]
    async for fact in global_collection.find(
        {"$text": {"$search": _final_prompt}}
    ).limit(2):
        if fact and (
            fact.get("expires_at") is None
            or fact["expires_at"] > datetime.now(timezone.utc)
        ):
            # Check if this is a public global fact
            fact_text = fact.get("fact_text", "")
            if "[SYSTEM_GLOBAL]" in fact_text:
                # Clean up the fact text for display
                clean_fact = fact_text.replace("[SYSTEM_GLOBAL]", "").replace("[SYSTEM_PRIVATE]", "")
                global_facts.append(clean_fact)
except Exception as e:
    logging.debug(f"Global fact search failed: {e}")

# Combine local and global facts
all_facts = global_facts + facts

if all_facts:
    knowledge_section = "Relevant knowledge:\n" + "\n".join(
        f"- {fact}" for fact in all_facts
    )
    _system_prompt += "\n\n" + knowledge_section
```

### Method 2: Test with Global Facts
1. **Inject a global fact** using the admin command:
   ```
   /inject_fact fact:"JakeyBot maintenance occurs every Sunday at 2 AM EST" category:"maintenance" expires_in:"never"
   ```

2. **Ask about the fact** in any conversation:
   ```
   @Jakey When does maintenance happen?
   ```

3. **Verify the response** includes the global fact information seamlessly integrated.

### Method 3: Test with User Memories
1. **Share personal information**:
   ```
   @Jakey Remember that I love pizza and I'm a developer
   ```

2. **Ask about yourself later**:
   ```
   @Jakey What do you know about me?
   ```

3. **Verify the response** recalls your personal information naturally.

## Key Integration Points

### Memory Tool Enhancements
The `Memory/tool.py` file was enhanced to prioritize global facts:
- Global facts are searched first using the special `guild_id = 0`
- Facts are clearly labeled by source (global vs. personal)
- Results are combined and presented naturally

### AI Model Integration
The `pollinations/infer.py` file includes:
- Automatic tool detection for memory needs
- Seamless integration of tool results into conversations
- Natural contextual responses after tool usage

### Chat Flow Integration
1. **Message Processing**: `generative_chat.py` processes incoming messages
2. **Knowledge Retrieval**: Searches both user and global knowledge bases
3. **System Prompt Enhancement**: Adds relevant facts to the AI context
4. **Response Generation**: AI uses all provided context naturally
5. **Memory Updates**: New information is automatically stored

## Verification Checklist

### ✅ Global Facts Working
- [ ] Global facts stored in `knowledge_0` collection
- [ ] Facts tagged with `[SYSTEM_GLOBAL]` prefix
- [ ] Searchable across all guilds and users
- [ ] Integrated into system prompts automatically
- [ ] Prioritized in search results

### ✅ User Memories Working
- [ ] Personal facts stored with `[Username]` prefix
- [ ] User-specific search functionality
- [ ] Automatic memory detection and storage
- [ ] Proactive memory usage in conversations
- [ ] Multi-user support with proper isolation

### ✅ Integration Working
- [ ] Combined fact search (global + user)
- [ ] Natural presentation in system prompts
- [ ] Seamless AI response generation
- [ ] No technical details exposed to users
- [ ] Contextual memory usage

## Troubleshooting

### If Facts Don't Appear
1. **Check MongoDB Connection**: Ensure `MONGO_DB_URL` is set in `dev.env`
2. **Verify Collection Creation**: Check that `knowledge_0` exists
3. **Test Search Functionality**: Use `/list_global_facts` to verify storage
4. **Check System Prompt**: Enable debug logging to see prompt construction

### If Integration Seems Broken
1. **Review Logs**: Check for errors in knowledge retrieval
2. **Test Direct Search**: Verify `search_facts` function works
3. **Check Prompt Length**: Ensure system prompt isn't truncated
4. **Verify Tool Loading**: Confirm Memory tool is properly initialized

## Best Practices for Testing

### Test Scenarios
1. **Global Announcements**: Inject and recall system-wide information
2. **User Preferences**: Store and recall personal information
3. **Mixed Queries**: Search terms that match both global and user facts
4. **Expiration Testing**: Verify expired facts are properly filtered
5. **Cross-Guild Testing**: Verify global facts work in different contexts

### Monitoring
- Enable debug logging to see knowledge retrieval process
- Monitor MongoDB collections for proper fact storage
- Test edge cases like empty searches and malformed data
- Verify proper cleanup of expired facts

## Conclusion

The memory and global facts integration is working correctly when:
- Global facts are accessible across all conversations
- User memories are properly associated and recalled
- Both types of information are seamlessly integrated into AI responses
- No technical implementation details are exposed to users
- The system handles expiration and cleanup properly

The enhancements made ensure that JakeyBot can leverage both global knowledge base and personal memories to provide rich, contextual responses while maintaining the natural conversational flow that defines the Jakey character.
