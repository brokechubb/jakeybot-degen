#!/usr/bin/env python3
"""
Script to reset JakeyBot database to a clean state.
This will delete all existing data and create a fresh database.
"""

import asyncio
import motor.motor_asyncio
import os


async def reset_database():
    """Delete the current database and create a fresh one"""
    print("🗑️ JakeyBot Database Reset Tool")
    print("=" * 40)

    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://127.0.0.1")
        await client.admin.command("ping")
        print("✅ Connected to MongoDB")

        # List all databases
        databases = await client.list_database_names()
        print(f"📚 Available databases: {databases}")

        # Check if jakey_prod_db exists
        if "jakey_prod_db" in databases:
            print(f"\n⚠️ Found existing database: jakey_prod_db")

            # Show what's in it
            db = client.jakey_prod_db
            collections = await db.list_collection_names()
            print(f"   Collections: {collections}")

            total_docs = 0
            for collection_name in collections:
                try:
                    count = await db[collection_name].count_documents({})
                    total_docs += count
                    print(f"   - {collection_name}: {count} documents")
                except Exception as e:
                    print(f"   - {collection_name}: Error counting - {e}")

            print(f"   Total documents: {total_docs}")

            # Confirm deletion
            print(f"\n🚨 WARNING: This will DELETE ALL DATA in jakey_prod_db!")
            print(f"Are you sure you want to continue? (yes/no): ", end="")

            try:
                response = input().lower().strip()
                if response not in ["yes", "y"]:
                    print("❌ Database reset cancelled")
                    return False
            except KeyboardInterrupt:
                print("\n❌ Database reset cancelled")
                return False

            # Drop the database
            print(f"\n🗑️ Dropping database: jakey_prod_db")
            await client.drop_database("jakey_prod_db")
            print(f"✅ Database dropped successfully")

        else:
            print(f"✅ No existing jakey_prod_db found")

        # Create fresh database
        print(f"\n🆕 Creating fresh database...")
        fresh_db = client.jakey_prod_db

        # Test the fresh database
        await fresh_db.command("ping")
        print(f"✅ Fresh database created and tested")

        # Verify it's empty
        collections = await fresh_db.list_collection_names()
        print(f"📚 Fresh database collections: {collections}")

        if not collections:
            print(f"✅ Database is completely clean and empty")
        else:
            print(f"⚠️ Unexpected collections found: {collections}")

        await client.close()
        print(f"\n🎉 Database reset completed successfully!")
        print(f"JakeyBot now has a completely fresh start!")

        return True

    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main function"""
    print("🚀 Starting database reset process...")

    success = await reset_database()

    if success:
        print("\n🎉 Database reset completed successfully!")
        print("Your JakeyBot now has a completely clean database!")
    else:
        print("\n💥 Database reset failed!")
        print("Check the error messages above.")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    # Run the reset
    asyncio.run(main())
