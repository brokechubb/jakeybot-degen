#!/usr/bin/env python3
"""Simple script to check MongoDB databases and collections"""

import asyncio
import motor.motor_asyncio
import os


async def check_databases():
    """Check what databases and collections exist"""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://127.0.0.1")

        # List all databases
        databases = await client.list_database_names()
        print(f"📚 Available databases: {databases}")

        # Check each database for collections
        for db_name in databases:
            if db_name not in ["admin", "local", "config"]:  # Skip system databases
                db = client[db_name]
                collections = await db.list_collection_names()
                print(f"📄 Database '{db_name}': {len(collections)} collections")

                if collections:
                    for collection in collections:
                        try:
                            count = await db[collection].count_documents({})
                            print(f"   - {collection}: {count} documents")
                        except Exception as e:
                            print(f"   - {collection}: Error counting - {e}")

        await client.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_databases())
