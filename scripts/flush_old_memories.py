#!/usr/bin/env python3
"""
Script to flush Jakey's old memory format and clean up the database
for the new user-specific memory system.

This script will:
1. Identify memories using the old format
2. Safely remove them from the database
3. Clean up any orphaned data
4. Report the cleanup results
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def flush_old_memories():
    """Flush old memory format from the database."""
    print("🧠 Jakey Memory Format Cleanup")
    print("=" * 50)

    try:
        # Import required modules
        from core.ai.history import History
        from motor.motor_asyncio import AsyncIOMotorClient
        from os import environ

        # Get database connection
        mongo_url = environ.get("MONGO_DB_URL")
        if not mongo_url:
            print("❌ MONGO_DB_URL not found in environment")
            return False

        db_name = environ.get("MONGO_DB_NAME", "jakey_prod_db")
        collection_name = environ.get(
            "MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection"
        )

        print(f"🔗 Connecting to MongoDB: {db_name}")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        collection = db[collection_name]

        # Get all guilds
        guilds = await collection.find({}).to_list(None)
        print(f"📊 Found {len(guilds)} guilds in database")

        total_old_memories = 0
        total_cleaned_guilds = 0

        for guild in guilds:
            guild_id = guild.get("guild_id")
            if not guild_id:
                continue

            print(f"\n🏠 Processing guild: {guild_id}")

            # Check knowledge collection for this guild
            knowledge_collection_name = f"knowledge_{guild_id}"
            if knowledge_collection_name in await db.list_collection_names():
                knowledge_collection = db[knowledge_collection_name]

                # Find old format memories (without user_id or with old structure)
                old_memories = []

                # Look for memories without user_id field (old format)
                async for memory in knowledge_collection.find(
                    {"user_id": {"$exists": False}}
                ):
                    old_memories.append(memory)

                # Look for memories with old text format (without [Username] prefix)
                async for memory in knowledge_collection.find(
                    {
                        "user_id": {"$exists": True},
                        "fact_text": {"$not": {"$regex": r"^\[.*?\]"}},
                    }
                ):
                    old_memories.append(memory)

                if old_memories:
                    print(f"  🧹 Found {len(old_memories)} old format memories")

                    # Delete old memories
                    result = await knowledge_collection.delete_many(
                        {"_id": {"$in": [mem["_id"] for mem in old_memories]}}
                    )

                    print(f"  ✅ Deleted {result.deleted_count} old memories")
                    total_old_memories += result.deleted_count
                    total_cleaned_guilds += 1
                else:
                    print(f"  ✅ No old format memories found")
            else:
                print(f"  ℹ️  No knowledge collection found")

        # Clean up any orphaned knowledge collections
        print(f"\n🧹 Cleaning up orphaned knowledge collections...")
        all_collections = await db.list_collection_names()
        knowledge_collections = [
            col for col in all_collections if col.startswith("knowledge_")
        ]

        orphaned_collections = []
        for knowledge_col in knowledge_collections:
            guild_id = knowledge_col.replace("knowledge_", "")

            # Check if this guild still exists in the main collection
            guild_exists = await collection.find_one({"guild_id": guild_id})
            if not guild_exists:
                orphaned_collections.append(knowledge_col)

        if orphaned_collections:
            print(
                f"  🗑️  Found {len(orphaned_collections)} orphaned knowledge collections"
            )
            for orphaned_col in orphaned_collections:
                await db.drop_collection(orphaned_col)
                print(f"    ✅ Dropped {orphaned_col}")
        else:
            print(f"  ✅ No orphaned collections found")

        # Summary
        print(f"\n" + "=" * 50)
        print(f"🎉 Memory Cleanup Complete!")
        print(f"📊 Results:")
        print(f"   • Total old memories removed: {total_old_memories}")
        print(f"   • Guilds cleaned: {total_cleaned_guilds}")
        print(f"   • Orphaned collections removed: {len(orphaned_collections)}")

        if total_old_memories > 0:
            print(f"\n✅ Successfully cleaned up old memory format!")
            print(
                f"   Jakey's memory system is now using the new user-specific format."
            )
            print(f"   All memories will now be properly associated with users.")
        else:
            print(f"\n✅ No old format memories were found!")
            print(f"   Jakey's memory system is already using the new format.")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during memory cleanup: {e}")
        return False


async def verify_new_format():
    """Verify that the new memory format is working correctly."""
    print(f"\n🔍 Verifying New Memory Format...")

    try:
        from core.ai.history import History
        from motor.motor_asyncio import AsyncIOMotorClient
        from os import environ

        mongo_url = environ.get("MONGO_DB_URL")
        if not mongo_url:
            print("❌ Cannot verify - MONGO_DB_URL not found")
            return False

        db_name = environ.get("MONGO_DB_NAME", "jakey_prod_db")
        collection_name = environ.get(
            "MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection"
        )

        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        collection = db[collection_name]

        # Check a few guilds for new format
        guilds = await collection.find({}).limit(3).to_list(None)

        for guild in guilds:
            guild_id = guild.get("guild_id")
            if not guild_id:
                continue

            knowledge_collection_name = f"knowledge_{guild_id}"
            if knowledge_collection_name in await db.list_collection_names():
                knowledge_collection = db[knowledge_collection_name]

                # Check for new format memories
                new_format_count = await knowledge_collection.count_documents(
                    {"user_id": {"$exists": True}, "fact_text": {"$regex": r"^\[.*?\]"}}
                )

                total_count = await knowledge_collection.count_documents({})

                if total_count > 0:
                    print(
                        f"  🏠 Guild {guild_id}: {new_format_count}/{total_count} memories use new format"
                    )
                else:
                    print(f"  🏠 Guild {guild_id}: No memories found")

        print(f"✅ Memory format verification complete")
        return True

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


async def main():
    """Main function to run the memory cleanup."""
    print("🧠 Jakey Memory Format Cleanup Tool")
    print(
        "This tool will clean up old memory format and prepare for new user-specific system."
    )
    print("=" * 50)

    # Confirm before proceeding
    response = input("Do you want to proceed with cleaning up old memories? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("❌ Operation cancelled by user")
        return False

    print(f"\n🚀 Starting memory cleanup...")

    # Run the cleanup
    success = await flush_old_memories()

    if success:
        # Verify the new format
        await verify_new_format()

        print(f"\n🎉 All done! Jakey's memory system is now clean and ready.")
        print(f"   New memories will be properly associated with users.")
        print(f"   Old format data has been safely removed.")
    else:
        print(f"\n❌ Memory cleanup failed. Please check the logs.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
