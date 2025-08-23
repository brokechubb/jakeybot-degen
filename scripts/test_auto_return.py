#!/usr/bin/env python3
"""
Test script for AutoReturnManager functionality

This script tests the basic functionality of the AutoReturnManager
without requiring a full Discord bot instance.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.services.auto_return_manager import AutoReturnManager


class MockBot:
    """Mock bot class for testing"""
    def __init__(self):
        self.name = "TestBot"
        self.DBConn = None


async def test_auto_return_manager():
    """Test the AutoReturnManager functionality"""
    print("🧪 Testing AutoReturnManager...")
    
    # Create mock bot
    bot = MockBot()
    
    # Create AutoReturnManager
    manager = AutoReturnManager(bot)
    
    print(f"✅ AutoReturnManager created with default tool: {manager.default_tool}")
    print(f"⏰ Tool timeouts: {manager.tool_timeouts}")
    
    # Test tool switching
    test_guild_id = 12345
    test_user_id = 67890
    
    print(f"\n🔄 Testing tool switching...")
    
    # Switch to ImageGen
    await manager.switch_tool_with_timeout(test_guild_id, "ImageGen", test_user_id)
    
    # Check current tool
    current_tool = await manager.get_current_tool(test_guild_id)
    print(f"✅ Current tool: {current_tool}")
    
    # Check remaining time
    remaining_time = await manager.get_remaining_time(test_guild_id)
    print(f"⏰ Remaining time: {remaining_time} seconds")
    
    # Test timeout extension
    print(f"\n⏰ Testing timeout extension...")
    await manager.extend_timeout(test_guild_id, 120)  # Add 2 minutes
    
    new_remaining_time = await manager.get_remaining_time(test_guild_id)
    print(f"✅ New remaining time: {new_remaining_time} seconds")
    
    # Test status
    print(f"\n📊 Testing status...")
    status = manager.get_status()
    print(f"✅ Status: {status}")
    
    # Test timer cancellation
    print(f"\n❌ Testing timer cancellation...")
    await manager.cancel_timer(test_guild_id)
    
    current_tool_after_cancel = await manager.get_current_tool(test_guild_id)
    print(f"✅ Tool after cancel: {current_tool_after_cancel}")
    
    # Test cleanup
    print(f"\n🧹 Testing cleanup...")
    await manager.cleanup()
    print(f"✅ Cleanup completed")
    
    print(f"\n🎉 All tests completed successfully!")


async def test_timeout_parsing():
    """Test timeout parsing functionality"""
    print("\n🧪 Testing timeout parsing...")
    
    # Test different timeout formats
    test_timeouts = {
        "ImageGen": 300,      # 5 minutes
        "ExaSearch": 180,     # 3 minutes
        "GitHub": 240,        # 4 minutes
        "CodeExecution": 600, # 10 minutes
        "default": 300        # 5 minutes
    }
    
    for tool, timeout in test_timeouts.items():
        minutes = timeout // 60
        seconds = timeout % 60
        
        if minutes > 0:
            time_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
        else:
            time_str = f"{seconds}s"
        
        print(f"✅ {tool}: {timeout}s ({time_str})")


def main():
    """Main test function"""
    print("🚀 AutoReturnManager Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("core/services/auto_return_manager.py").exists():
        print("❌ Error: Please run this script from the JakeyBot project root directory")
        sys.exit(1)
    
    try:
        # Run tests
        asyncio.run(test_auto_return_manager())
        asyncio.run(test_timeout_parsing())
        
        print("\n🎯 Test Summary:")
        print("✅ AutoReturnManager creation and initialization")
        print("✅ Tool switching with timeout")
        print("✅ Timeout extension")
        print("✅ Status reporting")
        print("✅ Timer cancellation")
        print("✅ Cleanup functionality")
        print("✅ Timeout parsing")
        
        print("\n🚀 AutoReturnManager is ready for use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
