#!/usr/bin/env python3
"""
Setup script for the Memory tool
"""

import os
import sys
from pathlib import Path


def get_available_tools():
    """Get list of available tools from the tools directory"""
    tools_dir = Path("tools")
    if not tools_dir.exists():
        return []

    available_tools = []
    for tool_dir in tools_dir.iterdir():
        if tool_dir.is_dir() and (tool_dir / "__init__.py").exists():
            available_tools.append(tool_dir.name)

    return sorted(available_tools)


def setup_memory_tool():
    """Set up the Memory tool as the default tool"""
    print("🧠 Setting up Memory Tool as default...")

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found. Please create one from dev.env.template first.")
        return False

    # Read current .env file
    try:
        with open(env_file, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

    # Check if DEFAULT_TOOL is already set to Memory
    if "DEFAULT_TOOL=Memory" in content:
        print("✅ Memory tool is already set as default!")
        return True

    # Get all available tools for replacement
    available_tools = get_available_tools()

    # Update DEFAULT_TOOL to Memory
    if "DEFAULT_TOOL=" in content:
        # Replace existing DEFAULT_TOOL with any available tool
        for tool in available_tools:
            content = content.replace(f"DEFAULT_TOOL={tool}", "DEFAULT_TOOL=Memory")
        # Also replace common variations
        content = content.replace("DEFAULT_TOOL=None", "DEFAULT_TOOL=Memory")
        content = content.replace("DEFAULT_TOOL=", "DEFAULT_TOOL=Memory")
    else:
        # Add DEFAULT_TOOL if it doesn't exist
        content += (
            "\n# Default tool to enable for new users/guilds\nDEFAULT_TOOL=Memory\n"
        )

    # Write updated content back to .env file
    try:
        with open(env_file, "w") as f:
            f.write(content)
        print("✅ Successfully set Memory tool as default!")
        return True
    except Exception as e:
        print(f"❌ Error writing to .env file: {e}")
        return False


def check_memory_tool_files():
    """Check if all Memory tool files exist"""
    print("🔍 Checking Memory tool files...")

    required_files = [
        "tools/Memory/__init__.py",
        "tools/Memory/manifest.py",
        "tools/Memory/tool.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All Memory tool files are present")
        return True


def show_available_tools():
    """Display all available tools"""
    tools = get_available_tools()
    if tools:
        print(f"\n📋 Available tools ({len(tools)}):")
        for tool in tools:
            print(f"   - {tool}")
    else:
        print("\n❌ No tools found in tools/ directory")


def main():
    """Main setup function"""
    print("🚀 JakeyBot Memory Tool Setup")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the JakeyBot root directory")
        return False

    # Show available tools
    show_available_tools()

    # Check Memory tool files
    if not check_memory_tool_files():
        print(
            "❌ Memory tool files are missing. Please ensure the tool is properly installed."
        )
        return False

    # Set up Memory tool as default
    if setup_memory_tool():
        print("\n🎉 Memory tool setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your bot to apply the changes")
        print("2. The Memory tool will now be enabled by default for new users/guilds")
        print("3. Existing users can enable it with: /feature Memory")
        print("4. Test it by saying: 'My name is [your name]'")
        print("5. Then ask: 'What's my name?' in a new conversation")
        print("\n🛠️  To change the default tool later, use:")
        print("   python scripts/set_default_tool.py <tool_name>")
        return True
    else:
        print("\n❌ Memory tool setup failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
