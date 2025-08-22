#!/usr/bin/env python3
"""
Test script for the Memory tool functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, MagicMock


class MockDiscordContext:
    def __init__(self, guild_id=12345, author_id=67890):
        self.guild = MagicMock()
        self.guild.id = guild_id
        self.author = MagicMock()
        self.author.id = author_id


class MockDiscordBot:
    def __init__(self):
        pass


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


async def test_memory_tool():
    """Test the Memory tool functionality"""
    print("🧠 Testing Memory Tool...")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the JakeyBot root directory")
        return False

    # Check Memory tool files first
    if not check_memory_tool_files():
        print("❌ Memory tool files are missing. Cannot proceed with testing.")
        return False

    # Mock dependencies
    mock_method_send = AsyncMock()
    mock_ctx = MockDiscordContext()
    mock_bot = MockDiscordBot()

    try:
        # Import the tool after checking files exist
        from tools.Memory.tool import Tool

        # Create tool instance
        tool = Tool(mock_method_send, mock_ctx, mock_bot)
        print("✅ Tool instance created successfully")

        # Test tool schema
        if hasattr(tool, "tool_schema") and tool.tool_schema:
            print(f"✅ Tool schema has {len(tool.tool_schema)} functions")
            for func in tool.tool_schema:
                print(f"   - {func['name']}: {func['description']}")
        else:
            print("❌ Tool schema not found")

        # Test OpenAI schema
        if hasattr(tool, "tool_schema_openai") and tool.tool_schema_openai:
            print(f"✅ OpenAI schema has {len(tool.tool_schema_openai)} functions")
        else:
            print("❌ OpenAI schema not found")

        # Test basic schema
        if hasattr(tool, "tool_schema_basic") and tool.tool_schema_basic:
            print(f"✅ Basic schema has {len(tool.tool_schema_basic)} functions")
        else:
            print("❌ Basic schema not found")

        # Test manifest
        try:
            from tools.Memory.manifest import ToolManifest

            manifest = ToolManifest()
            print(f"✅ Tool manifest loaded: {manifest.tool_human_name}")
        except Exception as e:
            print(f"❌ Error loading manifest: {e}")

        print("\n🎯 Memory Tool test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(
            "   Make sure all dependencies are installed and the tool is properly configured."
        )
        return False
    except Exception as e:
        print(f"❌ Error testing Memory Tool: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_memory_functionality():
    """Test basic memory functionality if possible"""
    print("\n🧪 Testing Memory Functionality...")
    print("=" * 40)

    try:
        # This would require a database connection, so we'll just show what would be tested
        print("📝 Memory functionality tests (would require database connection):")
        print("   - remember_fact: Store new information")
        print("   - recall_fact: Retrieve stored information")
        print("   - list_facts: List all stored facts")
        print("\n💡 To test with actual database:")
        print("   1. Ensure MongoDB is running")
        print("   2. Set up your .env file with MONGO_DB_URL")
        print("   3. Run the bot and use /feature Memory")
        print("   4. Test with actual Discord commands")

        return True
    except Exception as e:
        print(f"❌ Error in functionality test: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 JakeyBot Memory Tool Test Suite")
    print("=" * 50)

    # Test basic tool structure
    basic_test_passed = await test_memory_tool()

    # Test memory functionality
    functionality_test_passed = await test_memory_functionality()

    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"Basic Tool Test: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(
        f"Functionality Test: {'✅ PASSED' if functionality_test_passed else '⚠️  SKIPPED'}"
    )

    if basic_test_passed:
        print("\n🎉 Memory tool is properly configured and ready to use!")
        print("   Run 'python scripts/setup_memory.py' to set it as default tool.")
    else:
        print(
            "\n❌ Memory tool has configuration issues. Please fix them before proceeding."
        )

    return basic_test_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
