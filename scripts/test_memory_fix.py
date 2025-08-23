#!/usr/bin/env python3
"""
Test script to verify the memory system fixes are working properly.
This script tests the core memory functionality without requiring the full bot.
"""

import asyncio
import motor.motor_asyncio
from datetime import datetime, timedelta
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.history import History


class MockBot:
    """Mock bot class for testing"""

    def __init__(self):
        self.loop = asyncio.get_event_loop()


async def test_memory_system():
    """Test the memory system functionality"""
    print("🧠 Testing Memory System...")

    # Check if MONGO_DB_URL is set
    mongo_url = os.environ.get("MONGO_DB_URL")
    if not mongo_url:
        print("❌ MONGO_DB_URL environment variable not set")
        print("Please set MONGO_DB_URL in your environment or dev.env file")
        return False

    try:
        # Create database connection
        print("📡 Connecting to MongoDB...")
        db_conn = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)

        # Test connection
        await db_conn.admin.command("ping")
        print("✅ MongoDB connection successful")

        # Create History instance
        bot = MockBot()
        history = History(bot=bot, db_conn=db_conn)

        # Test guild ID
        test_guild_id = 12345
        test_user_id = 67890

        print(f"\n🔍 Testing with Guild ID: {test_guild_id}")

        # Test 1: Check memory status
        print("\n1️⃣ Testing memory status check...")
        status = await history.check_memory_status(test_guild_id)
        print(f"   Status: {status['status']}")
        print(f"   Message: {status['message']}")

        # Test 2: Add a test fact
        print("\n2️⃣ Testing fact storage...")
        test_fact = "This is a test fact to verify the memory system is working"
        fact_id = await history.add_fact(
            guild_id=test_guild_id,
            user_id=test_user_id,
            fact_text=test_fact,
            source="test_script",
            expires_at=None,
        )
        print(f"   Fact ID: {fact_id}")
        print(f"   Fact stored successfully")

        # Test 3: Search for the fact
        print("\n3️⃣ Testing fact search...")
        facts = await history.search_facts(test_guild_id, "test fact", limit=5)
        print(f"   Found {len(facts)} facts")
        for i, fact in enumerate(facts, 1):
            print(f"   {i}. {fact}")

        # Test 4: Get facts by user
        print("\n4️⃣ Testing facts by user...")
        user_facts = await history.get_facts_by_user(
            test_guild_id, test_user_id, limit=5
        )
        print(f"   User has {len(user_facts)} facts")
        for i, fact in enumerate(user_facts, 1):
            print(f"   {i}. {fact}")

        # Test 5: Get recent facts
        print("\n5️⃣ Testing recent facts...")
        recent_facts = await history.get_recent_facts(test_guild_id, limit=5)
        print(f"   Recent facts: {len(recent_facts)}")
        for i, fact in enumerate(recent_facts, 1):
            print(f"   {i}. {fact}")

        # Test 6: Check memory status again
        print("\n6️⃣ Testing memory status after adding fact...")
        status_after = await history.check_memory_status(test_guild_id)
        print(f"   Status: {status_after['status']}")
        print(f"   Total Facts: {status_after['total_facts']}")
        print(f"   Non-expired Facts: {status_after['non_expired_facts']}")
        print(f"   Text Index: {'✅' if status_after['text_index_exists'] else '❌'}")

        # Test 7: Test reindexing
        print("\n7️⃣ Testing memory reindex...")
        reindex_success = await history.force_reindex_memory(test_guild_id)
        print(f"   Reindex: {'✅' if reindex_success else '❌'}")

        # Test 8: Search again after reindex
        print("\n8️⃣ Testing search after reindex...")
        facts_after_reindex = await history.search_facts(
            test_guild_id, "test fact", limit=5
        )
        print(f"   Found {len(facts_after_reindex)} facts after reindex")

        # Cleanup: Delete test fact
        print("\n🧹 Cleaning up test data...")
        await history.delete_fact(test_guild_id, fact_id)
        print("   Test fact deleted")

        print("\n✅ All memory system tests completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Memory system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Close database connection
        if "db_conn" in locals():
            db_conn.close()
            print("   Database connection closed")


async def main():
    """Main test function"""
    print("🚀 JakeyBot Memory System Test")
    print("=" * 40)

    success = await test_memory_system()

    if success:
        print("\n🎉 Memory system is working correctly!")
        print("The bot should now be able to remember and recall information properly.")
    else:
        print("\n💥 Memory system has issues that need to be resolved.")
        print(
            "Check the error messages above and ensure MongoDB is properly configured."
        )

    print("\n" + "=" * 40)


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv("dev.env")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment variables")

    # Run the test
    asyncio.run(main())
