#!/usr/bin/env python3
"""
Tool Management Script for JakeyBot

This script helps you manage tools - view status, enable/disable tools,
and set default tools for users and guilds.

Usage:
    python scripts/manage_tools.py                    # Show all tools status
    python scripts/manage_tools.py enable <tool>     # Enable a tool
    python scripts/manage_tools.py disable <tool>    # Disable a tool
    python scripts/manage_tools.py status <tool>     # Show tool status
"""

import os
import sys
import asyncio
import motor.motor_asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_available_tools():
    """Get list of available tools from the tools directory"""
    tools_dir = Path("tools")
    if not tools_dir.exists():
        return []

    available_tools = []
    for tool_dir in tools_dir.iterdir():
        if tool_dir.is_dir() and (tool_dir / "__init__.py").exists():
            available_tools.append(tool_dir.name)

    return sorted(available_tools)


def get_tool_info(tool_name):
    """Get information about a specific tool"""
    tool_dir = Path("tools") / tool_name
    if not tool_dir.exists():
        return None

    info = {"name": tool_name, "exists": True, "files": [], "manifest": None}

    # Check required files
    required_files = ["__init__.py", "manifest.py", "tool.py"]
    for file in required_files:
        file_path = tool_dir / file
        if file_path.exists():
            info["files"].append(file)

    # Try to load manifest
    try:
        sys.path.insert(0, str(Path("tools")))
        manifest_module = __import__(f"{tool_name}.manifest", fromlist=["ToolManifest"])
        manifest_class = getattr(manifest_module, "ToolManifest")
        manifest = manifest_class()
        info["manifest"] = manifest
        sys.path.pop(0)
    except Exception:
        pass

    return info


async def get_database_tool_stats():
    """Get tool usage statistics from the database"""
    mongo_url = os.getenv("MONGO_DB_URL")
    if not mongo_url:
        return None

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        db_name = os.getenv("MONGO_DB_NAME", "jakey_prod_db")
        collection_name = os.getenv(
            "MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection"
        )

        db = client[db_name]
        collection = db[collection_name]

        # Get tool distribution
        pipeline = [{"$group": {"_id": "$tool_use", "count": {"$sum": 1}}}]
        tool_distribution = await collection.aggregate(pipeline).to_list(None)

        # Get total users
        total_users = await collection.count_documents({})

        client.close()

        return {"tool_distribution": tool_distribution, "total_users": total_users}
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
        return None


def show_tool_status(tool_name):
    """Show detailed status of a specific tool"""
    tool_info = get_tool_info(tool_name)
    if not tool_info:
        print(f"❌ Tool '{tool_name}' not found")
        return

    print(f"\n🔍 Tool Status: {tool_name}")
    print("=" * 40)

    # File status
    print("📁 Files:")
    required_files = ["__init__.py", "manifest.py", "tool.py"]
    for file in required_files:
        status = "✅" if file in tool_info["files"] else "❌"
        print(f"   {status} {file}")

    # Manifest info
    if tool_info["manifest"]:
        print(f"\n📋 Manifest:")
        print(f"   Name: {tool_info['manifest'].tool_human_name}")
        print(f"   Description: {tool_info['manifest'].memory_recall_description}")
        print(f"   Functions: {len(tool_info['tool_schema'])}")
    else:
        print("\n❌ Manifest could not be loaded")


def show_all_tools_status():
    """Show status of all available tools"""
    tools = get_available_tools()
    if not tools:
        print("❌ No tools found in tools/ directory")
        return

    print("🛠️  JakeyBot Tools Status")
    print("=" * 50)

    for tool in tools:
        tool_info = get_tool_info(tool)
        if tool_info:
            files_status = "✅" if len(tool_info["files"]) == 3 else "⚠️"
            manifest_status = "✅" if tool_info["manifest"] else "❌"
            print(f"{files_status} {tool:<20} {manifest_status} manifest")

    print(f"\n📊 Total tools: {len(tools)}")
    print("✅ = Complete, ⚠️ = Partial, ❌ = Missing")


async def show_database_stats():
    """Show tool usage statistics from database"""
    stats = await get_database_tool_stats()
    if not stats:
        return

    print("\n📊 Database Tool Usage")
    print("=" * 30)
    print(f"Total users: {stats['total_users']}")

    if stats["tool_distribution"]:
        print("\nTool distribution:")
        for tool in stats["tool_distribution"]:
            tool_name = tool["_id"] if tool["_id"] else "None (disabled)"
            count = tool["count"]
            percentage = (count / stats["total_users"]) * 100
            print(f"   {tool_name:<20} {count:>4} ({percentage:>5.1f}%)")


def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Show all tools status
        show_all_tools_status()
        asyncio.run(show_database_stats())
        return

    command = sys.argv[1].lower()

    if command == "status" and len(sys.argv) == 3:
        tool_name = sys.argv[2]
        show_tool_status(tool_name)
    elif command == "enable" and len(sys.argv) == 3:
        tool_name = sys.argv[2]
        print(f"🔄 To enable '{tool_name}' for all users, run:")
        print(f"   python scripts/set_default_tool.py {tool_name}")
    elif command == "disable" and len(sys.argv) == 3:
        print("🔄 To disable all tools for all users, run:")
        print("   python scripts/set_default_tool.py None")
    else:
        print("Usage:")
        print(
            "  python scripts/manage_tools.py                    # Show all tools status"
        )
        print("  python scripts/manage_tools.py status <tool>     # Show tool status")
        print(
            "  python scripts/manage_tools.py enable <tool>     # Show enable command"
        )
        print(
            "  python scripts/manage_tools.py disable           # Show disable command"
        )
        print("\nExamples:")
        print("  python scripts/manage_tools.py status Memory")
        print("  python scripts/manage_tools.py enable ImageGen")


if __name__ == "__main__":
    main()
