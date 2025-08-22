#!/usr/bin/env python3
"""
Database Flush Script for JakeyBot

This script flushes the MongoDB database by dropping the main collection
and all knowledge base collections. Use with caution!

Usage:
    python scripts/flush_db.py
"""

from dotenv import load_dotenv

load_dotenv()

import motor.motor_asyncio
from os import environ
import asyncio
import sys


def confirm_flush():
    """Get user confirmation before flushing the database"""
    print("⚠️  WARNING: This will permanently delete ALL data from your database!")
    print("=" * 70)
    print("This action cannot be undone.")
    print("\nThe following will be deleted:")
    print("  - All user/guild data")
    print("  - All conversation history")
    print("  - All knowledge base data")
    print("  - All tool usage statistics")

    response = input(
        "\nAre you absolutely sure you want to continue? (type 'YES' to confirm): "
    ).strip()
    return response == "YES"


async def main():
    """
    Flushes the MongoDB database by dropping the main collection and all knowledge base collections.
    """
    print("🗑️  JakeyBot Database Flush Tool")
    print("=" * 50)

    # Get user confirmation
    if not confirm_flush():
        print("❌ Database flush cancelled.")
        return

    try:
        # Get connection details from environment variables
        mongo_url = environ.get("MONGO_DB_URL")
        db_name = environ.get("MONGO_DB_NAME", "jakey_prod_db")
        collection_name = environ.get(
            "MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection"
        )

        if not mongo_url:
            print("❌ Error: MONGO_DB_URL environment variable not set.")
            print(
                "   Please check your .env file and ensure MONGO_DB_URL is configured."
            )
            return

        print(f"🔌 Connecting to MongoDB...")
        print(f"   Database: {db_name}")
        print(f"   Collection: {collection_name}")

        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        db = client[db_name]

        # Test connection
        try:
            await db.command("ping")
            print("✅ Successfully connected to MongoDB")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return

        # Get collection count before deletion
        try:
            main_count = await db[collection_name].count_documents({})
            print(f"📊 Main collection has {main_count} documents")
        except Exception as e:
            print(f"⚠️  Could not count documents in main collection: {e}")

        # Drop the main collection
        print(f"\n🗑️  Dropping main collection: {collection_name}")
        try:
            await db.drop_collection(collection_name)
            print("✅ Main collection dropped successfully")
        except Exception as e:
            print(f"❌ Error dropping main collection: {e}")

        # Drop knowledge base collections
        print("\n🗑️  Dropping knowledge base collections...")
        collections = await db.list_collection_names()
        knowledge_collections = [
            coll for coll in collections if coll.startswith("knowledge_")
        ]

        if knowledge_collections:
            for coll in knowledge_collections:
                try:
                    coll_count = await db[coll].count_documents({})
                    print(f"   Dropping {coll} ({coll_count} documents)...")
                    await db.drop_collection(coll)
                    print(f"   ✅ {coll} dropped successfully")
                except Exception as e:
                    print(f"   ❌ Error dropping {coll}: {e}")
        else:
            print("   ℹ️  No knowledge base collections found")

        # Show final status
        remaining_collections = await db.list_collection_names()
        print(f"\n📊 Database flush completed!")
        print(f"   Remaining collections: {len(remaining_collections)}")
        if remaining_collections:
            print(f"   Collections: {', '.join(remaining_collections)}")

        print("\n💡 Next steps:")
        print("   1. Restart your bot to ensure clean state")
        print("   2. New users will start with default tool settings")
        print("   3. All previous data has been permanently removed")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if "client" in locals():
            client.close()
            print("\n🔌 MongoDB connection closed")


if __name__ == "__main__":
    asyncio.run(main())
