# JakeyBot Scripts

This directory contains various utility scripts for managing and maintaining your JakeyBot instance.

## 📋 Available Scripts

### 🔧 Setup & Configuration

#### `setup_env.py`

Sets up your environment configuration file from the template.

```bash
python scripts/setup_env.py
```

**What it does:**

- Copies `dev.env.template` to `dev.env`
- Shows available AI models
- Provides setup guidance and security reminders

**Use when:** First-time setup or when you need to recreate your environment file

---

#### `setup_memory.py`

Sets up the Memory tool as the default tool for new users.

```bash
python scripts/setup_memory.py
```

**What it does:**

- Sets `DEFAULT_TOOL=Memory` in your `.env` file
- Checks that all Memory tool files are present
- Shows available tools in your system

**Use when:** You want to enable the Memory tool by default for all new users

---

### 🧪 Testing & Validation

#### `test_memory.py`

Tests the Memory tool functionality and configuration.

```bash
python scripts/test_memory.py
```

**What it does:**

- Verifies Memory tool files exist
- Tests tool instantiation and schemas
- Provides testing guidance for database functionality

**Use when:** You want to verify the Memory tool is working correctly

---

#### `security_check.py`

Scans your repository for potential security issues.

```bash
python scripts/security_check.py
```

**What it does:**

- Scans for hardcoded API keys and tokens
- Checks for sensitive file types
- Provides security recommendations

**Use when:** Before committing code or when you want to audit security

---

### 🗄️ Database Management

#### `flush_db.py`

**⚠️ DANGEROUS** - Completely clears your database.

```bash
python scripts/flush_db.py
```

**What it does:**

- Drops all user/guild data
- Removes all conversation history
- Deletes all knowledge base data
- Requires explicit confirmation

**Use when:** You need to completely reset your bot's data (development/testing only!)

---

#### `set_default_tool.py`

Sets the default tool for all existing users in the database.

```bash
python scripts/set_default_tool.py <tool_name>
python scripts/set_default_tool.py Memory
python scripts/set_default_tool.py ImageGen
python scripts/set_default_tool.py None
```

**What it does:**

- Updates all existing users to use a specific tool
- Shows current tool distribution statistics
- Dynamically detects available tools

**Use when:** You want to change the default tool for all existing users

---

### 🛠️ Management & Monitoring

#### `manage_tools.py`

Manages and monitors tool status.

```bash
python scripts/manage_tools.py                    # Show all tools status
python scripts/manage_tools.py status <tool>     # Show specific tool status
python scripts/manage_tools.py enable <tool>     # Show enable command
python scripts/manage_tools.py disable            # Show disable command
```

**What it does:**

- Shows status of all available tools
- Displays tool file completeness
- Shows database usage statistics
- Provides management guidance

**Use when:** You want to check tool status or get management help

---

#### `manage_ai_models.py`

Manages and monitors AI model configuration.

```bash
python scripts/manage_ai_models.py                    # Show all models
python scripts/manage_ai_models.py status <model>     # Show model status
python scripts/manage_ai_models.py config <model>     # Show config help
```

**What it does:**

- Shows status of all AI models
- Checks configuration completeness
- Provides setup guidance for each model
- Shows required environment variables

**Use when:** You want to check AI model status or get configuration help

---

## 🚀 Quick Start

1. **Initial Setup:**

   ```bash
   python scripts/setup_env.py
   # Edit your .env file with API keys
   python scripts/security_check.py
   ```

2. **Enable Memory Tool:**

   ```bash
   python scripts/setup_memory.py
   python scripts/test_memory.py
   ```

3. **Check System Status:**

   ```bash
   python scripts/manage_tools.py
   python scripts/manage_ai_models.py
   ```

4. **Change Default Tool:**

   ```bash
   python scripts/set_default_tool.py <tool_name>
   ```

## 🔒 Security Notes

- **Never commit your `.env` file** to version control
- Run `security_check.py` before committing code
- Keep API keys secure and private
- Use environment variables for all sensitive information

## 🛠️ Tool Management

### Available Tools

The scripts automatically detect tools from your `tools/` directory:

- **Memory** - Conversation memory and fact recall
- **ImageGen** - AI image generation
- **ExaSearch** - Web search capabilities
- **GitHub** - GitHub repository access
- **YouTube** - YouTube search and analysis
- **AudioTools** - Audio manipulation
- **IdeationTools** - Canvas and artifacts
- **CryptoPrice** - Live cryptocurrency prices
- **CurrencyConverter** - Live currency conversion
- **CodeExecution** - Python code execution

### AI Models

The scripts automatically detect AI models from your `aimodels/` directory:

- **OpenAI** - GPT models
- **Claude** - Anthropic models
- **Gemini** - Google models
- **Kimi** - Moonshot models
- **XAI** - Grok models
- **OpenRouter** - Multiple model access
- **Azure Foundry** - Azure OpenAI models

## 📚 Documentation

- **Configuration Guide:** `docs/CONFIG.md`
- **Security Guide:** `docs/SECURITY.md`
- **Tools Documentation:** `docs/TOOLS.md`
- **Memory Implementation:** `docs/MEMORY_IMPLEMENTATION.md`

## 🆘 Troubleshooting

### Common Issues

1. **"No .env file found"**
   - Run `python scripts/setup_env.py` first

2. **"MONGO_DB_URL not set"**
   - Check your `.env` file for MongoDB connection string

3. **"Tool files missing"**
   - Ensure the tool is properly installed in `tools/` directory

4. **"Import errors"**
   - Make sure you're running from the JakeyBot root directory
   - Check that all dependencies are installed

### Getting Help

- Check the documentation in the `docs/` directory
- Run scripts with no arguments to see usage information
- Use the status commands to diagnose issues:

  ```bash
  python scripts/manage_tools.py
  python scripts/manage_ai_models.py
  ```

## 🔄 Script Dependencies

All scripts require:

- Python 3.7+
- `python-dotenv` package
- `motor` package (for database scripts)
- Proper working directory (JakeyBot root)

Install dependencies with:

```bash
pip install python-dotenv motor
```
