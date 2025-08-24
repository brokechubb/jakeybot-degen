# JakeyBot Changelog

## [Unreleased]

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

---

## Contributing

When making changes, please:

1. Update this changelog
2. Follow the existing code style
3. Test your changes thoroughly
4. Update relevant documentation

---

*Maintainer: JakeyBot Team*
*Version: 2.0.0*
