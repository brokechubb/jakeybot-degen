# New `/model current` Command Summary

## 🆕 **What I Added**

I've added a new `/model current` command to show the current selected model for the server/guild.

## 📋 **Command Details**

### **Command**: `/model current`

- **Purpose**: Show the current default model for the server
- **Scope**: Guild-wide (affects entire server)
- **Response**: Ephemeral (only visible to the user who ran the command)

### **Command**: `/model set`

- **Purpose**: Set the default model for the server
- **Scope**: Guild-wide (affects entire server)
- **Permissions**: Administrator only
- **Response**: Ephemeral (only visible to the user who ran the command)

## 🎯 **Features**

### **Current Model Display**

- Shows the current model provider and name
- Displays server name (or "DM" for direct messages)
- Indicates whether the model has full features or basic capabilities

### **Feature Information**

- **✅ Full Features**: For models with real-time information, tool support, and web search
  - Providers: gemini, claude, openrouter, openai, kimi
- **⚠️ Basic Features**: For models with limited capabilities
  - Basic chat capabilities only
  - Limited real-time information
  - No tool support

### **Error Handling**

- Handles cases where no model is set (shows default)
- Handles invalid model formats in database
- Provides helpful error messages

## 📱 **Example Output**

### **When a model is set:**

```
🤖 Current Model
Server: My Discord Server
Provider: gemini
Model: gemini-2.5-flash

✅ Features
• Real-time information
• Tool support
• Web search capabilities

Use /model set to change the model
```

### **When no model is set:**

```
🤖 Current Model
No model set - Using system default

Use /model set to choose a specific model

Default: Gemini 2.5 Flash
```

## 🔧 **Technical Implementation**

### **Database Integration**

- Uses the existing `get_default_model()` method from the History class
- Respects the `SHARED_CHAT_HISTORY` setting
- Handles both guild and DM contexts

### **Model Parsing**

- Splits model string on "::" to extract provider and name
- Validates model format before display
- Handles edge cases gracefully

### **Embed Design**

- Clean, informative embed with color coding
- Green for models with full features
- Blue for default/no model set
- Includes helpful footer text

## 📚 **Updated Documentation**

### **Help Command**

Updated `/help` command to include the new model commands:

- `/model set <model>` - Switch AI models
- `/model current` - Show current model
- `/model list` - List all available models

## 🚀 **Usage**

Users can now:

1. **Check Current Model**: `/model current` to see what model is currently active
2. **Change Model**: `/model set <model>` to switch to a different model (Administrator only)
3. **List Models**: `/model list` to see all available options

## ✅ **Benefits**

1. **Transparency**: Users can see what model is currently active
2. **Debugging**: Helps troubleshoot model-related issues
3. **Coordination**: Server members can coordinate model changes
4. **Documentation**: Clear indication of current server settings
5. **User Experience**: Better understanding of available features
6. **Security**: Only administrators can change server-wide settings

## 🔒 **Administrator Requirements**

### **Why Administrator Only?**

- **Server-wide Impact**: Model changes affect all users in the server
- **Resource Management**: Different models have different costs and capabilities
- **Consistency**: Prevents conflicts from multiple users changing models
- **Security**: Protects against unauthorized model changes

### **Permission Check**

- **Guild Context**: Requires Administrator permission in Discord server
- **DM Context**: Works normally in direct messages (no guild permissions)
- **Error Handling**: Clear error messages for permission denied cases

## 🔄 **Integration**

The command integrates seamlessly with the existing model system:

- Works with all existing model providers
- Respects guild vs user settings
- Maintains consistency with other model commands
- Follows the same error handling patterns

The new `/model current` command provides much-needed visibility into the current model configuration and helps users understand what capabilities are available!
