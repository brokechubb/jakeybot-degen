# JakeyBot Changelog

## [Unreleased]

### Added

- **Auto-Return System**: Intelligent tool management with automatic activation and timeout management
- **Enhanced Engagement System**: Persistent engagement settings with MongoDB storage and configurable behavior
- **Gambling Games**: Interactive betting pools, trivia games, and keno number generation
- **Direct Image Generation**: No tool switching required for image creation and editing
- **Pollinations.AI Integration**: New AI provider with uncensored models and premium features
- **Smart Suggestions**: Context-aware optimization tips for tool usage and workflow efficiency
- **LavaLink v4 Music System**: Complete voice channel music functionality with queue management
- **Music Commands**: `/play`, `/pause`, `/resume`, `/stop`, `/skip`, `/queue`, `/volume`, `/nowplaying`, `/disconnect`
- **Vote-based Skipping**: Democratic music control with vote system
- **Music Queue Management**: Advanced queue system with shuffle and track management
- **Voice Channel Integration**: Seamless voice channel connection and management

### 🆘 Added

- **Enhanced Help System**: New `/help` and `/quickstart` slash commands
- **Comprehensive Help Guide**: Complete overview of all features, AI models, and tools
- **API Key Requirements**: Clear information about required API keys for each model
- **Troubleshooting Section**: Solutions for common issues and problems
- **Admin Command Reference**: Information about prefix commands for administrators
- **GitHub Repository Link**: Direct access to source code and documentation
- **Pollinations.AI Integration**: New AI provider with text and image generation capabilities
  - **Text Models**: OpenAI, Mistral, Claude, Gemini via Pollinations.AI
  - **Image Models**: Flux, Kontext (image-to-image), SDXL
  - **API Key Support**: Optional authentication for premium features (higher rate limits, no logo)
  - **Free Tier**: Works without API key for basic usage
  - **Image Generation**: Direct image generation with customizable parameters
- **Auto-Return System**: Intelligent tool management with automatic activation and timeout management
  - **Automatic Tool Activation**: Tools are automatically enabled when needed
  - **Smart Timeout Management**: Tools return to Memory after configurable timeouts
  - **Intelligent Suggestions**: Get optimization tips with `/smart_suggestions`
  - **Seamless Experience**: No manual tool management required
- **Enhanced Engagement System**: Persistent engagement settings with MongoDB storage
  - **MongoDB Persistence**: Engagement settings survive bot restarts
  - **Configurable Parameters**: Adjust engagement frequency and behavior via YAML
  - **Message Cooldown**: Prevent spam with intelligent timing
  - **Automatic Cleanup**: Remove invalid channels/guilds automatically
  - **Multi-Channel Support**: Engage in up to 50 channels simultaneously
- **Gambling Games**: Interactive community features
  - **Betting Pools**: Create community betting pools with voting
  - **Trivia Games**: AI-generated trivia questions with leaderboards
  - **Keno Numbers**: Generate random keno numbers
  - **Interactive Commands**: `/create_bet`, `/trivia`, `/keno`
- **Direct Image Generation**: No tool switching required
  - **Direct Commands**: `/generate_image` and `/edit_image`
  - **AI-Powered**: Uses advanced AI models for creation
  - **Multiple Models**: Support for various image generation models
  - **Advanced Editing**: Modify existing images with AI

### 🔧 Fixed

- **Discord Choice Limit**: Fixed `/model set` command exceeding Discord's 25-choice limit
  - **Priority Models**: OpenAI, Gemini, Claude, and Pollinations.AI models shown first
  - **Smart Limiting**: Automatically limits choices to 25 while preserving most important models
  - **Full List Available**: Use `/model list` to see all available models
- **Pollinations.AI Chat History**: Fixed TypeError when processing chat history with mixed data types
  - **Robust Parsing**: Handles time context strings and various message formats
  - **Error Handling**: Added comprehensive error handling and logging
  - **Backward Compatibility**: Works with existing chat history structures
- **Pollinations.AI System Prompt**: Fixed system prompt not being applied in chat conversations
  - **Proper System Prompt**: Now correctly applies Jakey's personality and identity
  - **Chat History Support**: System prompt is maintained across conversation history
  - **Fallback Prompt**: Includes proper Jakey system prompt when none is provided
- **Pollinations.AI 431 Error**: Fixed "Request Header Fields Too Large" error for long conversations
  - **Smart Endpoint Selection**: Automatically switches between GET and POST endpoints based on conversation length
  - **Private Parameter**: Added `private=true` parameter to prevent responses from appearing in public feed
  - **POST Endpoint Support**: Uses OpenAI-compatible POST endpoint for longer conversations with chat history
- **Pollinations.AI Content Filter**: Fixed Azure OpenAI content management policy filtering
  - **Uncensored Models**: Prioritizes "evil" and "unity" models which are marked as uncensored
  - **Model Fallback**: Automatically tries multiple models when content filters are triggered
  - **Smart Model Selection**: Uses actual available models from Pollinations.AI API
- **Pollinations.AI Models**: Comprehensive model list update based on actual API
  - **Uncensored Models**: Added "evil" and "unity" models for unfiltered responses
  - **Text Models**: Added 20+ new text generation models including OpenAI variants, Mistral, Llama, and more
  - **Community Models**: Added specialized models like BIDARA (NASA), MIDIjourney, and Mirexa
  - **Removed Unused**: Removed non-existent "claude" model from Pollinations.AI
- **Jakey Response Length**: Added guidelines for brief, punchy responses
  - **Target Length**: 1-3 sentences maximum for most responses
  - **Direct Communication**: Get to the point quickly, avoid rambling
  - **Natural Flow**: Keep conversations moving fast and engaging
  - **No Repetition**: Prevent saying the same thing multiple times in one response
- **Pollinations.AI Model Priority**: Fixed uncensored model prioritization
  - **Evil Model First**: Always tries "evil" uncensored model before others
  - **Smart Fallback**: Current model moved to position 3 if not uncensored
  - **No Content Filtering**: Eliminates unnecessary content filter errors
- **Documentation Updates**: Comprehensive documentation refresh
  - **Auto-Return Guide**: Complete guide for the new auto-return system
  - **Updated User Guides**: All user documentation updated with latest features
  - **Configuration Guide**: Enhanced configuration options for new features
  - **FAQ Updates**: Added sections for auto-return, engagement, and gambling features
  - **Tools Documentation**: Updated with auto-enablement and new tools

## [v2.1.0] - 2025-01-24

### 🎉 Added

- **Persistent Auto-Image Generation**: Auto-image settings now saved to database and survive bot restarts
- **Enhanced Image Generation Commands**: New `/auto_image_status` command and improved help system
- **Database-Backed Configuration**: All auto-image settings persist across restarts and server reboots

### 🔧 Changed

- **Memory System Cleanup**: Successfully flushed old memory format and transitioned to new user-specific system
- **Database Optimization**: Cleaned up orphaned knowledge collections and optimized memory storage
- **Enhanced Error Handling**: Better logging and error recovery for auto-image generation system

### 🧹 Cleaned Up

- **Old Memory Format**: Removed outdated memory structure that didn't associate memories with users
- **Orphaned Collections**: Cleaned up 1 orphaned knowledge collection from database
- **Memory Verification**: Confirmed 13/13 memories now use proper user-specific format

### 📊 Technical Improvements

- **Persistence Layer**: Added `_load_auto_image_settings()`, `_save_auto_image_setting()`, and related methods
- **New Guild Handling**: Automatic initialization of auto-image settings for new servers
- **Database Integration**: Seamless MongoDB integration for configuration persistence
- **Memory Format**: All memories now properly include `user_id` and `[Username]` prefix format

## [v2.0.0] - 2025-01-24

### 🎉 Added

- **Enhanced Configuration System**: Improved `assistants.yaml` with comprehensive settings
- **Multiple Personality Modes**: Jakey now supports various response styles (troll, degenerate_gambling, hypebeast, etc.)
- **Advanced Error Handling**: User-friendly error messages and fallback responses
- **Performance Optimizations**: Better temperature, token limits, and response handling
- **Persistent Engagement System**: Engagement settings now survive bot restarts with MongoDB storage
- **Enhanced Engagement Features**:
  - MongoDB persistence for engagement settings
  - Configurable engagement parameters via YAML
  - Message cooldown system to prevent spam
  - Automatic cleanup of invalid channels/guilds
  - Support for up to 50 simultaneous engagements
  - New commands: status, list, and statistics
- **On-Demand Image Generation**: Direct image generation commands without AI tool usage required
- **Automatic Image Detection**: Jakey automatically detects image requests and offers generation options
- **Smart Prompt Extraction**: Automatically extracts image descriptions from natural language requests

### 🔧 Changed

- **Configuration Structure**: Consolidated all assistant settings into single `assistants.yaml` file
- **Memory System**: Fixed user memory contamination and implemented proper user-specific memory recall
- **Gemini API Compatibility**: Resolved multiple compatibility issues with google-generativeai library
- **Project Structure**: Cleaned up unused files, scripts, and test artifacts
- **Documentation**: Updated README, CHANGELOG, and removed references to deleted files

### 🐛 Fixed

- **Memory User Association**: Memories now properly linked to creating users, preventing cross-user confusion
- **Gemini API Errors**: Fixed Part.from_text() method signature and GenerationConfig type compatibility issues
- **API Key Configuration**: Added proper API key validation and configuration for image generation
- **Memory Priority System**: Implemented 4-tier priority system for user-specific memory recall

### 🗑️ Removed

- **Unused Files**: Removed test scripts, old modular configuration, and database artifacts
- **Modular Config**: Consolidated assistant configuration back to single file due to bot compatibility
- **Temporary Scripts**: Cleaned up migration and test scripts after successful implementation

### 📚 Documentation

- **Updated README**: Reflects v2.0.0 features and project cleanup
- **Enhanced CHANGELOG**: Comprehensive documentation of all changes and improvements
- **Security Updates**: Fixed documentation examples that triggered pre-commit hooks

## [1.x.x] - Previous Versions

### Legacy Features

- Multi-model AI support (Gemini, OpenAI, Claude, etc.)
- Discord bot functionality
- Gambling and crypto expertise
- Image generation and audio manipulation
- Security enhancements and environment management

---

## Migration Guide

### From v1.x to v2.0.0

**No Breaking Changes**: All existing functionality is preserved.

**What Changed**:

- Configuration is now in single `assistants.yaml` file
- Project structure cleaned up for better maintainability

**What You Need to Do**:

1. **Nothing!** The bot will work exactly as before
2. **Optional**: Customize Jakey's personality in `assistants.yaml`

### From v2.0.0 to v2.1.0

**New Features**:

- Auto-return system for intelligent tool management
- Enhanced engagement system with persistence
- Gambling games and interactive features
- Direct image generation commands
- Pollinations.AI integration

**What You Need to Do**:

1. **Update configuration**: Add new environment variables for auto-return and engagement
2. **Install dependencies**: Ensure `PyNaCl` is installed for voice support
3. **Configure API keys**: Add Pollinations.AI API key if desired
4. **Test new features**: Try auto-return system and engagement features

---

## Contributing

When making changes, please:

1. Update this changelog
2. Follow the existing code style
3. Test your changes thoroughly
4. Update relevant documentation

---

*Maintainer: JakeyBot Team*
*Version: 2.1.0*
