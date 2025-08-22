#!/usr/bin/env python3
"""
Script to set the default tool for all existing users/guilds in the database.
This is useful when you want to enable a tool by default for all users.
"""

import asyncio
import motor.motor_asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv("dev.env")


async def set_default_tool_for_all_users(tool_name: str):
    """Set the default tool for all existing users/guilds"""

    # Get MongoDB connection details
    mongo_url = os.getenv("MONGO_DB_URL")
    db_name = os.getenv("MONGO_DB_NAME", "jakey_prod_db")
    collection_name = os.getenv("MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection")

    if not mongo_url:
        print("❌ MONGO_DB_URL not set in dev.env")
        sys.exit(1)

    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    collection = db[collection_name]

    try:
        # Update all documents to set the default tool
        result = await collection.update_many(
            {},  # Update all documents
            {"$set": {"tool_use": tool_name}},
        )

        print(
            f"✅ Successfully updated {result.modified_count} users/guilds to use '{tool_name}' as default tool"
        )

        # Show current tool distribution
        pipeline = [{"$group": {"_id": "$tool_use", "count": {"$sum": 1}}}]

        tool_distribution = await collection.aggregate(pipeline).to_list(None)

        print("\n📊 Current tool distribution:")
        for tool in tool_distribution:
            tool_name_display = tool["_id"] if tool["_id"] else "None (disabled)"
            print(f"  {tool_name_display}: {tool['count']} users")

    except Exception as e:
        print(f"❌ Error updating database: {e}")
        sys.exit(1)
    finally:
        client.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_default_tool.py <tool_name>")
        print("\nAvailable tools:")
        print("  ImageGen - Image generation and editing")
        print("  ExaSearch - Web search")
        print("  GitHub - GitHub repository access")
        print("  YouTube - YouTube search and analysis")
        print("  AudioTools - Audio manipulation")
        print("  IdeationTools - Canvas and artifacts")
        print("  CryptoPrice - Live crypto prices")
        print("  CurrencyConverter - Live currency conversion")
        print("  CodeExecution - Python code execution")
        print("  None - Disable all tools")
        sys.exit(1)

    tool_name = sys.argv[1]

    # Validate tool name
    valid_tools = [
        "ImageGen",
        "ExaSearch",
        "GitHub",
        "YouTube",
        "AudioTools",
        "IdeationTools",
        "CryptoPrice",
        "CurrencyConverter",
        "CodeExecution",
        "None",
    ]

    if tool_name not in valid_tools:
        print(f"❌ Invalid tool name: {tool_name}")
        print(f"Valid options: {', '.join(valid_tools)}")
        sys.exit(1)

    # Convert "None" to None for database
    if tool_name == "None":
        tool_name = None

    print(f"🔄 Setting default tool to: {tool_name or 'None (disabled)'}")

    # Run the async function
    asyncio.run(set_default_tool_for_all_users(tool_name))


if __name__ == "__main__":
    main()
