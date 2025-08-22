# 🔒 Security Guide

This document provides comprehensive guidance on keeping your personal information and API keys secure when using JakeyBot.

## 🚨 Critical Security Measures

### 1. Environment Variables

**NEVER commit your `dev.env` file to version control!**

- Copy `dev.env.template` to `dev.env`
- Fill in your actual API keys and tokens in `dev.env`
- The `dev.env` file is already in `.gitignore` to prevent accidental commits

### 2. API Keys and Tokens

Keep these secure and never share them:

- **Discord Bot Token**: Your bot's authentication token
- **OpenAI API Key**: For GPT models (starts with `sk-`)
- **Google API Keys**: For Gemini models (starts with `AIza`)
- **GitHub Token**: For GitHub integration (starts with `ghp_`)
- **YouTube API Key**: For YouTube search (starts with `AIza`)
- **MongoDB Connection String**: Database connection with credentials

### 3. Database Security

- Never commit database files (`.db`, `.sqlite`, etc.)
- Use environment variables for database connection strings
- Consider using connection string encryption for production

## 🛡️ Security Features

### Pre-commit Hook

A pre-commit hook is installed that automatically checks for:

- API keys and tokens in code
- Environment files being committed
- Database files being committed
- Common sensitive data patterns

The hook will block commits if it detects potential sensitive information.

### Comprehensive .gitignore

The `.gitignore` file includes:

- All environment files (`*.env`, `dev.env`)
- API key files (`*.key`, `*.pem`, etc.)
- Database files (`*.db`, `.sqlite`)
- Log files (`*.log`)
- Virtual environments (`venv/`, `.venv/`)
- IDE files (`.vscode/`, `.idea/`)

## 🚨 Common Security Mistakes to Avoid

### ❌ Don't do this

```python
# Hardcoding API keys in code
api_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
```

### ✅ Do this instead

```python
# Using environment variables
import os
api_key = os.environ.get("OPENAI_API_KEY")
```

### ❌ Don't commit

- `dev.env` files with real credentials
- Database files with user data
- Log files that might contain sensitive information
- Configuration files with passwords

### ✅ Safe to commit

- `dev.env.template` (template files)
- Code that reads from environment variables
- Documentation and README files
- Test files (without real credentials)

## 🔍 Checking for Sensitive Information

### Before committing, check

1. **API Keys**: Look for patterns like `sk-`, `ghp_`, `AIza`
2. **Connection Strings**: Check for URLs with credentials
3. **Environment Files**: Ensure `.env` files aren't being committed
4. **Database Files**: Verify no `.db` or `.sqlite` files are included

### Manual check command

```bash
# Check for API keys in your code
grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=venv --exclude-dir=.git

# Check for GitHub tokens
grep -r "ghp_[a-zA-Z0-9]" . --exclude-dir=venv --exclude-dir=.git

# Check for Google API keys
grep -r "AIza[0-9A-Za-z-_]" . --exclude-dir=venv --exclude-dir=.git
```

## 🚨 If You Accidentally Commit Sensitive Information

### Immediate Actions

1. **Don't panic** - act quickly
2. **Revoke the exposed credentials** immediately
3. **Generate new credentials** to replace the old ones
4. **Update your environment variables** with the new credentials

### Remove from Git History

```bash
# Remove file from git history (use with caution)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch dev.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to remove from remote repository
git push origin --force --all
```

## 🔐 Production Security

### For production deployments

1. **Use environment variables** or secure secret management
2. **Rotate API keys regularly**
3. **Use least-privilege access** for all services
4. **Monitor for unusual activity**
5. **Keep dependencies updated**

### Docker Security

```bash
# Use environment file for Docker
docker run --env-file dev.env your-image

# Or pass environment variables directly
docker run -e TOKEN=your-token -e OPENAI_API_KEY=your-key your-image
```

## 📞 Getting Help

If you discover a security vulnerability:

1. **Don't create a public issue** with sensitive information
2. **Contact the maintainer privately** if possible
3. **Include minimal reproduction steps** without exposing credentials

## ✅ Security Checklist

Before pushing to GitHub:

- [ ] No API keys in code
- [ ] No `dev.env` file committed
- [ ] No database files committed
- [ ] No log files with sensitive data
- [ ] Pre-commit hook passes
- [ ] Environment variables used for all secrets
- [ ] Template files don't contain real credentials

Remember: **When in doubt, don't commit it!** It's always better to be overly cautious with sensitive information.
