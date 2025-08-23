#!/usr/bin/env python3
"""
Simple database backup script for JakeyBot.
Creates compressed backups of the entire database.
"""

import asyncio
import motor.motor_asyncio
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def backup_database():
    """Create a backup of the JakeyBot database"""
    print("💾 JakeyBot Database Backup Tool")
    print("=" * 40)

    # Check if MONGO_DB_URL is set
    mongo_url = os.environ.get("MONGO_DB_URL")
    if not mongo_url:
        print("❌ MONGO_DB_URL environment variable not set")
        print("Please set MONGO_DB_URL in your environment or dev.env file")
        return False

    try:
        # Parse MongoDB connection details
        if mongo_url.startswith("mongodb://"):
            # Remove mongodb:// prefix
            connection_string = mongo_url[10:]
        elif mongo_url.startswith("mongodb+srv://"):
            # Remove mongodb+srv:// prefix
            connection_string = mongo_url[14:]
        else:
            print("❌ Invalid MongoDB URL format")
            return False

        # Extract database name
        if "/" in connection_string:
            db_name = connection_string.split("/")[-1].split("?")[0]
        else:
            print("❌ Could not extract database name from URL")
            return False

        print(f"📡 Database: {db_name}")
        print(f"🔗 Connection: {mongo_url[:20]}...")

        # Test connection
        print("\n🔍 Testing database connection...")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        await client.admin.command("ping")
        print("✅ Database connection successful")

        # Create backup directory
        backup_dir = Path("database_backups")
        backup_dir.mkdir(exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"jakeybot_backup_{db_name}_{timestamp}"
        backup_path = backup_dir / backup_filename

        print(f"\n💾 Creating backup: {backup_filename}")

        # Check if mongodump is available
        try:
            subprocess.run(["mongodump", "--version"], capture_output=True, check=True)
            print("✅ mongodump found, using native backup")

            # Create backup using mongodump
            cmd = [
                "mongodump",
                "--uri",
                mongo_url,
                "--db",
                db_name,
                "--out",
                str(backup_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Backup completed successfully!")

                # Compress the backup
                print("🗜️ Compressing backup...")
                import tarfile

                tar_filename = f"{backup_filename}.tar.gz"
                tar_path = backup_dir / tar_filename

                with tarfile.open(tar_path, "w:gz") as tar:
                    tar.add(backup_path, arcname=backup_filename)

                # Remove uncompressed backup
                import shutil

                shutil.rmtree(backup_path)

                print(f"✅ Compressed backup saved: {tar_filename}")
                print(f"📁 Location: {tar_path.absolute()}")

                # Show backup size
                size_mb = tar_path.stat().st_size / (1024 * 1024)
                print(f"📊 Size: {size_mb:.2f} MB")

                return True

            else:
                print(f"❌ Backup failed: {result.stderr}")
                return False

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ mongodump not found, using Python-based backup")

            # Fallback: Python-based backup
            collections = await client[db_name].list_collection_names()
            print(f"📚 Found {len(collections)} collections")

            backup_data = {}
            total_documents = 0

            for collection_name in collections:
                try:
                    collection = client[db_name][collection_name]
                    documents = await collection.find({}).to_list(None)

                    # Convert ObjectId to string for JSON serialization
                    for doc in documents:
                        if "_id" in doc:
                            doc["_id"] = str(doc["_id"])
                        # Convert datetime objects
                        for key, value in doc.items():
                            if hasattr(value, "isoformat"):
                                doc[key] = value.isoformat()

                    backup_data[collection_name] = documents
                    total_documents += len(documents)
                    print(f"   📄 {collection_name}: {len(documents)} documents")

                except Exception as e:
                    print(f"   ❌ Error backing up {collection_name}: {e}")

            # Save backup
            backup_file = backup_path.with_suffix(".json")
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            # Compress
            import gzip

            gz_filename = f"{backup_filename}.json.gz"
            gz_path = backup_dir / gz_filename

            with open(backup_file, "rb") as f_in:
                with gzip.open(gz_path, "wb") as f_out:
                    f_out.writelines(f_in)

            # Remove uncompressed backup
            backup_file.unlink()

            print(f"✅ Python backup completed: {gz_filename}")
            print(f"📁 Location: {gz_path.absolute()}")
            print(f"📊 Total documents: {total_documents}")

            return True

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if "client" in locals():
            client.close()


async def restore_backup(backup_file: str):
    """Restore a database backup"""
    print("🔄 JakeyBot Database Restore Tool")
    print("=" * 40)

    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False

    # Check if MONGO_DB_URL is set
    mongo_url = os.environ.get("MONGO_DB_URL")
    if not mongo_url:
        print("❌ MONGO_DB_URL environment variable not set")
        return False

    try:
        # Extract database name
        if mongo_url.startswith("mongodb://"):
            connection_string = mongo_url[10:]
        elif mongo_url.startswith("mongodb+srv://"):
            connection_string = mongo_url[14:]
        else:
            print("❌ Invalid MongoDB URL format")
            return False

        if "/" in connection_string:
            db_name = connection_string.split("/")[-1].split("?")[0]
        else:
            print("❌ Could not extract database name from URL")
            return False

        print(f"📡 Target database: {db_name}")
        print(f"📁 Backup file: {backup_file}")

        # Confirm restore
        print("\n⚠️ WARNING: This will overwrite the existing database!")
        print("Are you sure you want to continue? (yes/no): ", end="")

        try:
            response = input().lower().strip()
            if response not in ["yes", "y"]:
                print("❌ Restore cancelled")
                return False
        except KeyboardInterrupt:
            print("\n❌ Restore cancelled")
            return False

        # Test connection
        print("\n🔍 Testing database connection...")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        await client.admin.command("ping")
        print("✅ Database connection successful")

        if backup_path.suffix == ".tar.gz":
            # Restore from mongodump backup
            print("🔄 Restoring from mongodump backup...")

            # Extract backup
            import tarfile

            extract_dir = backup_path.parent / backup_path.stem
            extract_dir.mkdir(exist_ok=True)

            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(extract_dir)

            # Find the extracted backup directory
            backup_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if not backup_dirs:
                print("❌ No backup directory found in archive")
                return False

            backup_dir = backup_dirs[0]

            # Use mongorestore
            try:
                cmd = [
                    "mongorestore",
                    "--uri",
                    mongo_url,
                    "--db",
                    db_name,
                    "--drop",  # Drop existing collections
                    str(backup_dir),
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print("✅ Restore completed successfully!")

                    # Cleanup
                    import shutil

                    shutil.rmtree(extract_dir)

                    return True
                else:
                    print(f"❌ Restore failed: {result.stderr}")
                    return False

            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ mongorestore not found, cannot restore this backup type")
                return False

        elif backup_path.suffix == ".gz":
            # Restore from Python backup
            print("🔄 Restoring from Python backup...")

            import gzip

            with gzip.open(backup_path, "rt", encoding="utf-8") as f:
                backup_data = json.load(f)

            # Drop existing collections
            for collection_name in backup_data.keys():
                try:
                    await client[db_name][collection_name].drop()
                    print(f"   🗑️ Dropped collection: {collection_name}")
                except Exception as e:
                    print(f"   ⚠️ Could not drop {collection_name}: {e}")

            # Restore collections
            total_restored = 0
            for collection_name, documents in backup_data.items():
                if documents:
                    try:
                        # Convert string IDs back to ObjectId
                        from bson import ObjectId

                        for doc in documents:
                            if "_id" in doc and isinstance(doc["_id"], str):
                                try:
                                    doc["_id"] = ObjectId(doc["_id"])
                                except:
                                    pass  # Keep as string if not valid ObjectId

                        result = await client[db_name][collection_name].insert_many(
                            documents
                        )
                        restored_count = len(result.inserted_ids)
                        total_restored += restored_count
                        print(
                            f"   ✅ {collection_name}: {restored_count} documents restored"
                        )

                    except Exception as e:
                        print(f"   ❌ Error restoring {collection_name}: {e}")

            print(f"\n✅ Restore completed! Total documents: {total_restored}")
            return True

        else:
            print(f"❌ Unsupported backup format: {backup_path.suffix}")
            return False

    except Exception as e:
        print(f"❌ Restore failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if "client" in locals():
            client.close()


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="JakeyBot Database Backup Tool")
    parser.add_argument("--restore", help="Restore from backup file")
    args = parser.parse_args()

    if args.restore:
        success = await restore_backup(args.restore)
    else:
        success = await backup_database()

    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n💥 Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv("dev.env")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment variables")

    # Run the backup/restore
    asyncio.run(main())
