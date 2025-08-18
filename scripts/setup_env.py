#!/usr/bin/env python3
"""
Environment Setup Script for JakeyBot

This script helps you set up your dev.env file securely from the template.
It will guide you through the process and ensure no sensitive information is exposed.

Usage:
    python scripts/setup_env.py
"""

import os
import shutil
from pathlib import Path


def main():
    """Main function to set up the environment file."""
    print("🔧 JakeyBot Environment Setup")
    print("=" * 50)
    print("This script will help you set up your dev.env file securely.")
    print("It will copy the template and guide you through the configuration.\n")

    # Get the repository root
    repo_root = Path(__file__).parent.parent
    template_file = repo_root / "dev.env.template"
    env_file = repo_root / "dev.env"

    # Check if template exists
    if not template_file.exists():
        print("❌ Error: dev.env.template not found!")
        print(f"   Expected location: {template_file}")
        return 1

    # Check if dev.env already exists
    if env_file.exists():
        print("⚠️  Warning: dev.env file already exists!")
        response = input("   Do you want to overwrite it? (y/N): ").strip().lower()
        if response != "y":
            print("   Setup cancelled.")
            return 0

    try:
        # Copy template to dev.env
        shutil.copy2(template_file, env_file)
        print(f"✅ Created {env_file}")

        print(f"\n📝 Next steps:")
        print(f"   1. Edit {env_file} with your actual API keys and tokens")
        print(f"   2. Make sure to set your Discord bot TOKEN")
        print(f"   3. Configure any additional API keys you want to use")
        print(f"   4. Run 'python scripts/security_check.py' to verify security")

        print(f"\n🔒 Security reminders:")
        print(f"   - Never commit dev.env to version control")
        print(f"   - Keep your API keys secure and private")
        print(f"   - Rotate keys regularly for production use")
        print(f"   - See docs/SECURITY.md for detailed guidelines")

        print(f"\n📚 Documentation:")
        print(f"   - Configuration guide: docs/CONFIG.md")
        print(f"   - Security guide: docs/SECURITY.md")
        print(f"   - Tools documentation: docs/TOOLS.md")

        return 0

    except Exception as e:
        print(f"❌ Error creating dev.env file: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
