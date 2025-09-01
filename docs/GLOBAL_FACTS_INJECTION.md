# Global Facts Injection System

This document explains how to inject important facts into JakeyBot's global knowledge base that can be accessed in conversations across all guilds and users.

## Overview

The global facts injection system allows bot owners to store important information that JakeyBot can reference in any conversation. This is useful for:
- Bot-wide announcements
- Important policies or rules
- System information
- Frequently asked questions
- General knowledge that should be available everywhere

## Commands

### `/inject_fact` (Owner Only)
Injects important facts into the global knowledge base.

**Parameters:**
- `fact` (required): The fact or information to remember
- `category` (optional, default: "global"): Category for organizing the fact
- `expires_in` (optional, default: "never"): Expiration time (e.g., '1d', '2h', '30m', 'never' for permanent)
- `make_public` (optional, default: True): Whether the fact should be accessible to all users

**Example Usage:**
```
/inject_fact fact:"The bot maintenance window is every Sunday at 2 AM EST" category:"maintenance" expires_in:"never"
```

### `/list_global_facts` (Owner Only)
Lists all global facts in the knowledge base.

**Parameters:**
- `limit` (optional, default: 10): Maximum number of facts to display

**Example Usage:**
```
/list_global_facts limit:20
```

## How It Works

1. **Global Storage**: Facts are stored in a special MongoDB collection with `guild_id = 0`
2. **System Tagging**: Global facts are tagged with `[SYSTEM_GLOBAL]` for identification
3. **Priority Access**: When users search for facts, global facts are checked first
4. **Expiration Handling**: Global facts can be set to expire automatically
5. **Category Organization**: Facts can be organized by categories for better management

## Technical Implementation

### Database Structure
Global facts are stored in the `knowledge_0` collection in MongoDB with the following structure:
```json
{
  "_id": "unique_fact_id",
  "user_id": "admin_user_id",
  "fact_text": "[SYSTEM_GLOBAL][category] The actual fact text",
  "source": "admin_injection/user_id",
  "created_at": "timestamp",
  "last_accessed_at": "timestamp",
  "expires_at": "optional_expiration_timestamp"
}
```

### Memory Tool Integration
The Memory tool has been enhanced to:
1. First search the global knowledge base (`knowledge_0` collection)
2. Prioritize global facts in search results
3. Clearly indicate when information comes from the global knowledge base

## Usage Examples

### Adding Bot Information
```
/inject_fact fact:"JakeyBot is an advanced AI Discord bot created for gaming and productivity" category:"bot_info" expires_in:"never"
```

### Adding Maintenance Schedule
```
/inject_fact fact:"Weekly maintenance occurs every Sunday at 2 AM EST. The bot may be temporarily unavailable during this time." category:"maintenance" expires_in:"never"
```

### Adding Temporary Announcement
```
/inject_fact fact:"New image generation features are now available! Try the /generate_image command." category:"announcements" expires_in:"7d"
```

## Accessing Global Facts

Users can access global facts through the Memory tool:
- When using `/recall` or natural conversation, global facts will be automatically included
- Global facts are clearly labeled as coming from the "global knowledge base"
- The system prioritizes global facts alongside user-specific memories

## Security and Permissions

- Only bot owners can inject global facts
- Only bot owners can list global facts
- All global fact operations are logged
- Facts are stored securely in the database with proper indexing

## Best Practices

1. **Keep it Relevant**: Only inject facts that are truly global and useful everywhere
2. **Use Categories**: Organize facts with appropriate categories for better management
3. **Set Expirations**: Use expiration times for temporary information
4. **Be Clear**: Write facts in a clear, concise manner that's easy to understand
5. **Avoid Sensitive Data**: Never store sensitive or private information as global facts

## Troubleshooting

### Facts Not Appearing
- Ensure the MongoDB connection is properly configured
- Check that the facts were successfully injected using `/list_global_facts`
- Verify that the Memory tool is enabled for the conversation

### Database Issues
- Check MongoDB connection strings in `dev.env`
- Ensure the database is accessible and running
- Verify sufficient disk space and memory

## Future Enhancements

- Automatic fact categorization
- Fact validation and duplicate detection
- Bulk import/export functionality
- Web interface for managing global facts
- Advanced search and filtering options
