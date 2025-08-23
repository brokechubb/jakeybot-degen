#!/usr/bin/env python3
"""
Database dump and analysis script for JakeyBot memory system.
This script provides comprehensive database inspection, backup, and analysis capabilities.
"""

import asyncio
import motor.motor_asyncio
from datetime import datetime, timedelta
import os
import sys
import json
import csv
from pathlib import Path
from collections import defaultdict

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.history import History


class MockBot:
    """Mock bot class for testing"""

    def __init__(self):
        self.loop = asyncio.get_event_loop()


class DatabaseAnalyzer:
    """Analyze and dump JakeyBot database contents"""

    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.client = None
        self.db = None
        self.history = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_url)
            await self.client.admin.command("ping")

            # Get the database name from the URL
            if "/" in self.mongo_url and not self.mongo_url.endswith("/"):
                db_name = self.mongo_url.split("/")[-1].split("?")[0]
                if db_name == "127.0.0.1" or db_name == "localhost":
                    db_name = "jakeybot"  # Default database name
            else:
                db_name = "jakeybot"  # Default database name
            self.db = self.client[db_name]

            # Create History instance for analysis
            bot = MockBot()
            self.history = History(bot=bot, db_conn=self.client)

            print(f"✅ Connected to database: {db_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False

    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("📡 Database connection closed")

    async def analyze_database_structure(self):
        """Analyze the overall database structure"""
        print("\n🔍 Analyzing Database Structure...")

        try:
            # Get all collections
            collections = await self.db.list_collection_names()
            print(f"📚 Found {len(collections)} collections:")

            collection_stats = {}
            total_documents = 0

            for collection_name in collections:
                try:
                    collection = self.db[collection_name]
                    doc_count = await collection.count_documents({})
                    total_documents += doc_count

                    # Get collection size info
                    stats = await collection.aggregate(
                        [
                            {
                                "$group": {
                                    "_id": None,
                                    "totalSize": {"$sum": {"$bsonSize": "$$ROOT"}},
                                }
                            }
                        ]
                    ).to_list(1)

                    size_bytes = stats[0]["totalSize"] if stats else 0
                    size_mb = size_bytes / (1024 * 1024)

                    collection_stats[collection_name] = {
                        "documents": doc_count,
                        "size_mb": round(size_mb, 2),
                    }

                    print(
                        f"   📄 {collection_name}: {doc_count} documents, {size_mb:.2f} MB"
                    )

                except Exception as e:
                    print(f"   ❌ Error analyzing {collection_name}: {e}")

            print(f"\n📊 Total: {total_documents} documents across all collections")
            return collection_stats

        except Exception as e:
            print(f"❌ Error analyzing database structure: {e}")
            return {}

    async def analyze_memory_collections(self):
        """Analyze memory-related collections specifically"""
        print("\n🧠 Analyzing Memory Collections...")

        memory_stats = {}

        try:
            # Find all knowledge collections
            collections = await self.db.list_collection_names()
            knowledge_collections = [
                c for c in collections if c.startswith("knowledge_")
            ]
            reminder_collections = [
                c for c in collections if c.startswith("reminders_")
            ]

            print(f"📚 Found {len(knowledge_collections)} knowledge collections")
            print(f"⏰ Found {len(reminder_collections)} reminder collections")

            # Analyze each knowledge collection
            for collection_name in knowledge_collections:
                try:
                    collection = self.db[collection_name]

                    # Basic stats
                    total_facts = await collection.count_documents({})

                    # Count by expiration status
                    now = datetime.utcnow()
                    expired_facts = await collection.count_documents(
                        {"expires_at": {"$lt": now}}
                    )

                    non_expired_facts = await collection.count_documents(
                        {
                            "$or": [
                                {"expires_at": {"$exists": False}},
                                {"expires_at": None},
                                {"expires_at": {"$gt": now}},
                            ]
                        }
                    )

                    # Count by source
                    source_stats = await collection.aggregate(
                        [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
                    ).to_list(None)

                    # Check for text index
                    indexes = await collection.list_indexes().to_list(None)
                    has_text_index = any(
                        index.get("key", {}).get("fact_text") == "text"
                        for index in indexes
                    )

                    memory_stats[collection_name] = {
                        "total_facts": total_facts,
                        "expired_facts": expired_facts,
                        "non_expired_facts": non_expired_facts,
                        "source_stats": {s["_id"]: s["count"] for s in source_stats},
                        "has_text_index": has_text_index,
                        "indexes": [index.get("name") for index in indexes],
                    }

                    print(f"   📄 {collection_name}:")
                    print(
                        f"      Total: {total_facts}, Active: {non_expired_facts}, Expired: {expired_facts}"
                    )
                    print(f"      Text Index: {'✅' if has_text_index else '❌'}")

                    if source_stats:
                        sources_text = ", ".join(
                            [f"{s['_id']}: {s['count']}" for s in source_stats[:3]]
                        )
                        print(f"      Sources: {sources_text}")

                except Exception as e:
                    print(f"   ❌ Error analyzing {collection_name}: {e}")

            return memory_stats

        except Exception as e:
            print(f"❌ Error analyzing memory collections: {e}")
            return {}

    async def export_memory_data(self, output_dir: str = "database_dumps"):
        """Export all memory data to files"""
        print(f"\n💾 Exporting Memory Data to {output_dir}...")

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            collections = await self.db.list_collection_names()
            knowledge_collections = [
                c for c in collections if c.startswith("knowledge_")
            ]
            reminder_collections = [
                c for c in collections if c.startswith("reminders_")
            ]

            exported_files = []

            # Export knowledge collections
            for collection_name in knowledge_collections:
                try:
                    collection = self.db[collection_name]

                    # Get all documents
                    documents = await collection.find({}).to_list(None)

                    if documents:
                        # Export as JSON
                        json_file = output_path / f"{collection_name}_{timestamp}.json"
                        with open(json_file, "w", encoding="utf-8") as f:
                            # Convert ObjectId to string for JSON serialization
                            for doc in documents:
                                if "_id" in doc:
                                    doc["_id"] = str(doc["_id"])
                                if "expires_at" in doc and doc["expires_at"]:
                                    doc["expires_at"] = doc["expires_at"].isoformat()
                                if "created_at" in doc:
                                    doc["created_at"] = doc["created_at"].isoformat()
                                if "last_accessed_at" in doc:
                                    doc["last_accessed_at"] = doc[
                                        "last_accessed_at"
                                    ].isoformat()

                            json.dump(documents, f, indent=2, ensure_ascii=False)

                        # Export as CSV
                        csv_file = output_path / f"{collection_name}_{timestamp}.csv"
                        if documents:
                            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                                if documents:
                                    fieldnames = list(documents[0].keys())
                                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                                    writer.writeheader()
                                    writer.writerows(documents)

                        exported_files.extend([json_file, csv_file])
                        print(
                            f"   ✅ Exported {collection_name}: {len(documents)} documents"
                        )

                except Exception as e:
                    print(f"   ❌ Error exporting {collection_name}: {e}")

            # Export reminder collections
            for collection_name in reminder_collections:
                try:
                    collection = self.db[collection_name]
                    documents = await collection.find({}).to_list(None)

                    if documents:
                        json_file = output_path / f"{collection_name}_{timestamp}.json"
                        with open(json_file, "w", encoding="utf-8") as f:
                            for doc in documents:
                                if "_id" in doc:
                                    doc["_id"] = str(doc["_id"])
                                if "remind_time" in doc:
                                    doc["remind_time"] = doc["remind_time"].isoformat()
                                if "created_at" in doc:
                                    doc["created_at"] = doc["created_at"].isoformat()

                            json.dump(documents, f, indent=2, ensure_ascii=False)

                        exported_files.append(json_file)
                        print(
                            f"   ✅ Exported {collection_name}: {len(documents)} reminders"
                        )

                except Exception as e:
                    print(f"   ❌ Error exporting {collection_name}: {e}")

            # Create summary report
            summary_file = output_path / f"dump_summary_{timestamp}.txt"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"JakeyBot Database Dump Summary\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Database: {self.mongo_url}\n\n")

                f.write(f"Collections Found:\n")
                f.write(f"Knowledge: {len(knowledge_collections)}\n")
                f.write(f"Reminders: {len(reminder_collections)}\n\n")

                f.write(f"Exported Files:\n")
                for file in exported_files:
                    f.write(f"- {file.name}\n")

            exported_files.append(summary_file)
            print(f"\n📁 Exported {len(exported_files)} files to {output_path}")
            return exported_files

        except Exception as e:
            print(f"❌ Error during export: {e}")
            return []

    async def analyze_memory_health(self):
        """Analyze the overall health of the memory system"""
        print("\n🏥 Analyzing Memory System Health...")

        try:
            collections = await self.db.list_collection_names()
            knowledge_collections = [
                c for c in collections if c.startswith("knowledge_")
            ]

            if not knowledge_collections:
                print(
                    "   ⚠️ No knowledge collections found - memory system may not be initialized"
                )
                return False

            health_issues = []
            total_facts = 0
            total_expired = 0
            collections_with_indexes = 0

            for collection_name in knowledge_collections:
                collection = self.db[collection_name]

                # Count facts
                fact_count = await collection.count_documents({})
                total_facts += fact_count

                if fact_count == 0:
                    health_issues.append(f"Collection {collection_name} is empty")

                # Count expired facts
                now = datetime.utcnow()
                expired_count = await collection.count_documents(
                    {"expires_at": {"$lt": now}}
                )
                total_expired += expired_count

                # Check text index
                indexes = await collection.list_indexes().to_list(None)
                has_text_index = any(
                    index.get("key", {}).get("fact_text") == "text" for index in indexes
                )

                if has_text_index:
                    collections_with_indexes += 1
                else:
                    health_issues.append(
                        f"Collection {collection_name} missing text index"
                    )

            # Health assessment
            print(f"   📊 Total Facts: {total_facts}")
            print(f"   ⏰ Expired Facts: {total_expired}")
            print(
                f"   🔍 Collections with Text Index: {collections_with_indexes}/{len(knowledge_collections)}"
            )

            if health_issues:
                print(f"\n   ⚠️ Health Issues Found:")
                for issue in health_issues:
                    print(f"      - {issue}")

                if total_expired > total_facts * 0.5:
                    print(
                        f"      - High percentage of expired facts ({total_expired}/{total_facts})"
                    )

                if collections_with_indexes < len(knowledge_collections):
                    print(f"      - Missing text indexes will cause search failures")

                return False
            else:
                print(f"\n   ✅ Memory system appears healthy!")
                return True

        except Exception as e:
            print(f"❌ Error analyzing memory health: {e}")
            return False

    async def cleanup_expired_facts(self, dry_run: bool = True):
        """Clean up expired facts from the database"""
        print(f"\n🧹 Cleaning Up Expired Facts (Dry Run: {dry_run})...")

        try:
            collections = await self.db.list_collection_names()
            knowledge_collections = [
                c for c in collections if c.startswith("knowledge_")
            ]

            total_expired = 0
            total_cleaned = 0

            for collection_name in knowledge_collections:
                collection = self.db[collection_name]

                # Find expired facts
                now = datetime.utcnow()
                expired_facts = await collection.find(
                    {"expires_at": {"$lt": now}}
                ).to_list(None)

                if expired_facts:
                    total_expired += len(expired_facts)
                    print(
                        f"   📄 {collection_name}: {len(expired_facts)} expired facts"
                    )

                    if not dry_run:
                        # Actually delete expired facts
                        result = await collection.delete_many(
                            {"expires_at": {"$lt": now}}
                        )
                        total_cleaned += result.deleted_count
                        print(f"      🗑️ Deleted {result.deleted_count} expired facts")
                    else:
                        print(
                            f"      👀 Would delete {len(expired_facts)} expired facts (dry run)"
                        )

            if total_expired == 0:
                print("   ✅ No expired facts found")
            else:
                if dry_run:
                    print(
                        f"\n   📋 Summary: {total_expired} expired facts would be cleaned up"
                    )
                    print(
                        "   💡 Run with dry_run=False to actually clean up expired facts"
                    )
                else:
                    print(f"\n   🗑️ Cleaned up {total_cleaned} expired facts")

            return total_expired

        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return 0


async def main():
    """Main function"""
    print("🚀 JakeyBot Database Analysis & Dump Tool")
    print("=" * 50)

    # Check if MONGO_DB_URL is set
    mongo_url = os.environ.get("MONGO_DB_URL")
    if not mongo_url:
        print("❌ MONGO_DB_URL environment variable not set")
        print("Please set MONGO_DB_URL in your environment or dev.env file")
        return

    # Create analyzer
    analyzer = DatabaseAnalyzer(mongo_url)

    try:
        # Connect to database
        if not await analyzer.connect():
            return

        # Analyze database structure
        collection_stats = await analyzer.analyze_database_structure()

        # Analyze memory collections
        memory_stats = await analyzer.analyze_memory_collections()

        # Analyze memory health
        is_healthy = await analyzer.analyze_memory_health()

        # Export data
        exported_files = await analyzer.export_memory_data()

        # Cleanup analysis (dry run)
        expired_count = await analyzer.cleanup_expired_facts(dry_run=True)

        # Summary
        print("\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Database Collections: {len(collection_stats)}")
        print(
            f"Memory Collections: {len([c for c in collection_stats.keys() if c.startswith('knowledge_')])}"
        )
        print(
            f"Total Documents: {sum(stats['documents'] for stats in collection_stats.values())}"
        )
        print(
            f"Memory System Health: {'✅ Healthy' if is_healthy else '⚠️ Issues Found'}"
        )
        print(f"Expired Facts: {expired_count}")
        print(f"Exported Files: {len(exported_files)}")

        if exported_files:
            print(f"\n📁 Files exported to: {exported_files[0].parent}")
            print("Files include:")
            for file in exported_files:
                print(f"  - {file.name}")

        if not is_healthy:
            print(f"\n🔧 RECOMMENDATIONS:")
            print("1. Run /memory_reindex in Discord to fix missing text indexes")
            print("2. Check bot logs for specific error messages")
            print("3. Verify MongoDB connection and permissions")
            print(
                "4. Consider running cleanup with dry_run=False to remove expired facts"
            )

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        await analyzer.disconnect()


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv("dev.env")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment variables")

    # Run the analysis
    asyncio.run(main())
