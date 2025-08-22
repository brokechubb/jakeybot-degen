#!/usr/bin/env python3
"""
Security Check Script for JakeyBot

This script scans the repository for potential sensitive information
like API keys, tokens, and other credentials that should not be committed.

Usage:
    python scripts/security_check.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns to check for sensitive information
SENSITIVE_PATTERNS = [
    # OpenAI API keys
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
    # Azure OpenAI API keys
    (r"sk-[a-zA-Z0-9]{32}", "Azure OpenAI API Key"),
    # Claude API keys
    (r"sk-ant-[a-zA-Z0-9]{48}", "Claude API Key"),
    # Gemini API keys
    (r"AIza[0-9A-Za-z-_]{35}", "Google/Gemini API Key"),
    (r"AIzaSy[0-9A-Za-z\-_]{22}", "Google API Key (Alternative)"),
    # Kimi API keys
    (r"kimi-[a-zA-Z0-9]{32,}", "Kimi API Key"),
    # XAI API keys
    (r"xai-[a-zA-Z0-9]{32,}", "XAI API Key"),
    # OpenRouter API keys
    (r"sk-or-[a-zA-Z0-9]{32,}", "OpenRouter API Key"),
    # GitHub tokens
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghu_[a-zA-Z0-9]{36}", "GitHub User-to-Server Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub Server-to-Server Token"),
    (r"ghr_[a-zA-Z0-9]{36}", "GitHub Refresh Token"),
    # Google OAuth tokens
    (r"ya29\.[0-9A-Za-z\-_]+", "Google OAuth Token"),
    (r"1//[0-9A-Za-z\-_]+", "Google OAuth Refresh Token"),
    # Discord tokens
    (r"[MN][a-zA-Z0-9]{23}\.[\w-]{6}\.[\w-]{27}", "Discord Bot Token"),
    # Slack tokens
    (r"xoxb-[a-zA-Z0-9\-]+", "Slack Bot Token"),
    (r"xoxp-[a-zA-Z0-9\-]+", "Slack User Token"),
    (r"xoxa-[a-zA-Z0-9\-]+", "Slack App Token"),
    (r"xoxr-[a-zA-Z0-9\-]+", "Slack App-Level Token"),
    # Exa Search API keys
    (r"exa-[a-zA-Z0-9]{32,}", "Exa Search API Key"),
    # Generic bearer tokens
    (r"Bearer [a-zA-Z0-9\-_\.]{20,}", "Bearer Token"),
    # Connection strings with credentials
    (r"mongodb://[^@]+@[^/]+", "MongoDB Connection String with Credentials"),
    (r"mongodb\+srv://[^@]+@[^/]+", "MongoDB Atlas Connection String with Credentials"),
    (r"postgresql://[^@]+@[^/]+", "PostgreSQL Connection String with Credentials"),
    (r"mysql://[^@]+@[^/]+", "MySQL Connection String with Credentials"),
    (r"redis://[^@]+@[^/]+", "Redis Connection String with Credentials"),
    # Hardcoded assignments
    (r'password\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Password"),
    (r'secret\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Secret"),
    (r'token\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Token"),
    (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded API Key"),
    (r'api_secret\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded API Secret"),
    (r'client_id\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Client ID"),
    (r'client_secret\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Client Secret"),
]

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".git",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "build",
    "dist",
    ".venv",
    "env",
    "ENV",
    ".env",
}

# Files to exclude from scanning (documentation examples, etc.)
EXCLUDE_FILES = {
    "docs/SECURITY.md",  # Contains example patterns for documentation
    "scripts/security_check.py",  # Contains regex patterns for scanning
}

# File extensions to exclude
EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".flac",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}


def should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped during scanning."""
    # Skip excluded directories
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return True

    # Skip excluded files
    relative_path = str(file_path.relative_to(Path(__file__).parent.parent))
    if relative_path in EXCLUDE_FILES:
        return True

    # Skip excluded file extensions
    if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
        return True

    # Skip binary files (basic check)
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:  # Contains null bytes
                return True
    except (IOError, OSError):
        return True

    return False


def scan_file(file_path: Path) -> List[Tuple[str, str, int]]:
    """Scan a single file for sensitive patterns."""
    findings = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern, description in SENSITIVE_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Mask the sensitive part for display
                        matched_text = match.group(0)
                        if len(matched_text) > 10:
                            masked_text = (
                                matched_text[:4]
                                + "*" * (len(matched_text) - 8)
                                + matched_text[-4:]
                            )
                        else:
                            masked_text = "*" * len(matched_text)

                        findings.append((description, masked_text, line_num))
    except (IOError, OSError, UnicodeDecodeError):
        pass

    return findings


def scan_repository(repo_path: Path) -> dict:
    """Scan the entire repository for sensitive information."""
    results = {"files_scanned": 0, "findings": [], "sensitive_files": []}

    print(f"🔍 Scanning repository: {repo_path}")
    print("=" * 50)

    # Check for sensitive file types
    sensitive_file_patterns = [
        "*.env",
        "*.key",
        "*.pem",
        "*.p12",
        "*.pfx",
        "*.crt",
        "*.cer",
        "*.der",
        "*.p7b",
        "*.p7c",
        "*.jks",
        "*.keystore",
        "*.db",
        "*.sqlite",
    ]

    for pattern in sensitive_file_patterns:
        for file_path in repo_path.rglob(pattern):
            if not should_skip_file(file_path):
                relative_path = file_path.relative_to(repo_path)
                results["sensitive_files"].append(str(relative_path))

    # Scan all text files
    for file_path in repo_path.rglob("*"):
        if file_path.is_file() and not should_skip_file(file_path):
            results["files_scanned"] += 1

            findings = scan_file(file_path)
            if findings:
                relative_path = file_path.relative_to(repo_path)
                results["findings"].append(
                    {"file": str(relative_path), "findings": findings}
                )

    return results


def print_results(results: dict):
    """Print the scan results in a formatted way."""
    print(f"\n📊 Scan Results:")
    print(f"Files scanned: {results['files_scanned']}")
    print(f"Files with potential issues: {len(results['findings'])}")
    print(f"Sensitive file types found: {len(results['sensitive_files'])}")

    if results["sensitive_files"]:
        print(f"\n⚠️  Sensitive file types detected:")
        for file_path in results["sensitive_files"]:
            print(f"   - {file_path}")

    if results["findings"]:
        print(f"\n🚨 Potential sensitive information found:")
        for file_result in results["findings"]:
            print(f"\n📁 File: {file_result['file']}")
            for description, masked_text, line_num in file_result["findings"]:
                print(f"   Line {line_num}: {description} - {masked_text}")
    else:
        print(f"\n✅ No sensitive information detected!")

    print(f"\n💡 Recommendations:")
    if results["sensitive_files"]:
        print("   - Review sensitive file types and ensure they're in .gitignore")
    if results["findings"]:
        print("   - Review findings and remove any hardcoded credentials")
        print("   - Use environment variables instead of hardcoded values")
    else:
        print("   - Your repository appears to be secure!")
        print("   - Continue using environment variables for all secrets")


def main():
    """Main function to run the security check."""
    repo_path = Path(__file__).parent.parent

    print("🔒 JakeyBot Security Check")
    print("=" * 50)
    print("This script scans for potential sensitive information in your repository.")
    print(
        "It looks for API keys, tokens, and other credentials that should not be committed.\n"
    )

    results = scan_repository(repo_path)
    print_results(results)

    # Exit with error code if issues found
    if results["findings"] or results["sensitive_files"]:
        print(
            f"\n❌ Security issues detected. Please review and fix before committing."
        )
        sys.exit(1)
    else:
        print(f"\n✅ Security check passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
