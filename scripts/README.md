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

#### `test_memory_fix.py`

Tests memory system fixes and improvements.

```bash
python scripts/test_memory_fix.py
```

**What it does:**

- Tests memory system fixes and improvements
- Validates database connection and functionality
- Checks memory tool performance

**Use when:** You want to test memory system fixes or validate improvements

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

#### `backup_database.py`

Creates a complete backup of your database.

```bash
python scripts/backup_database.py
```

**What it does:**

- Exports all database collections to JSON files
- Creates timestamped backup files
- Stores backups in `database_backups/` directory
- Includes user data, conversation history, and knowledge base

**Use when:** Before major updates or when you want to preserve your data

---

#### `check_databases.py`

Checks the status and health of your databases.

```bash
python scripts/check_databases.py
```

**What it does:**

- Verifies database connections
- Checks collection counts and sizes
- Reports database health status
- Identifies potential issues

**Use when:** Troubleshooting database problems or monitoring system health

---

#### `database_dump.py`

Creates detailed dumps of specific database collections.

```bash
python scripts/database_dump.py
```

**What it does:**

- Exports specific collections to CSV/JSON formats
- Creates detailed analysis reports
- Generates data summaries
- Useful for data analysis and debugging

**Use when:** You need detailed analysis of specific data or debugging issues

---

#### `reset_database.py`

Resets specific parts of your database.

```bash
python scripts/reset_database.py
```

**What it does:**

- Resets specific collections or data types
- Preserves other data while clearing selected areas
- Safer alternative to complete database flush
- Interactive confirmation for each reset operation

**Use when:** You need to clear specific data without losing everything

---

### 🛠️ Tool & Model Management

#### `manage_tools.py`

Manages and checks the status of available tools.

```bash
python scripts/manage_tools.py
python scripts/manage_tools.py status <tool_name>
```

**What it does:**

- Lists all available tools
- Shows tool status and configuration
- Checks tool dependencies
- Provides tool management options

**Use when:** You want to check tool status or troubleshoot tool issues

---

#### `manage_ai_models.py`

Manages and checks AI model configurations.

```bash
python scripts/manage_ai_models.py
python scripts/manage_ai_models.py config <model_name>
```

**What it does:**

- Lists all available AI models
- Shows model configurations and status
- Checks API key availability
- Provides model management options

**Use when:** You want to check model status or troubleshoot model issues

---

#### `set_default_tool.py`

Sets a default tool for all users.

```bash
python scripts/set_default_tool.py <tool_name>
```

**What it does:**

- Sets a default tool for all existing users
- Updates user preferences in bulk
- Useful for server-wide tool configuration
- Supports all available tools

**Use when:** You want to change the default tool for all users

---

## 🚀 Quick Start

### **First Time Setup**

1. **Set up environment:**
   ```bash
   python scripts/setup_env.py
   ```

2. **Configure API keys** in the generated `dev.env` file

3. **Set up Memory tool:**
   ```bash
   python scripts/setup_memory.py
   ```

4. **Verify security:**
   ```bash
   python scripts/security_check.py
   ```

### **Regular Maintenance**

- **Check database health:** `python scripts/check_databases.py`
- **Backup data:** `python scripts/backup_database.py`
- **Test memory system:** `python scripts/test_memory.py`

### **Troubleshooting**

- **Tool issues:** `python scripts/manage_tools.py`
- **Model problems:** `python scripts/manage_ai_models.py`
- **Memory issues:** `python scripts/test_memory_fix.py`

---

## ⚠️ **Important Notes**

### **Security**

- **Never commit** `dev.env` files
- **Always run** `security_check.py` before committing
- **Backup data** before major changes
- **Test scripts** in development environment first

### **Database Operations**

- **Backup first** before any destructive operations
- **Test scripts** on development data
- **Verify permissions** before running database scripts
- **Monitor logs** during database operations

### **Tool Management**

- **One tool active** per conversation
- **Test tools** after configuration changes
- **Check dependencies** before enabling tools
- **Monitor performance** when switching tools

---

## 📚 **Additional Resources**

- **[Main README](../README.md)** - Complete project overview
- **[Configuration Guide](../docs/CONFIG.md)** - Detailed setup instructions
- **[Security Guide](../docs/SECURITY.md)** - Security best practices
- **[Tools Documentation](../docs/TOOLS.md)** - Tool usage and configuration

---

**🔧 These scripts help you manage and maintain your JakeyBot instance effectively. Always backup your data before making major changes!**
