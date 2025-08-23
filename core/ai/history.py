from core.exceptions import HistoryDatabaseError
from core.services.helperfunctions import HelperFunctions
from os import environ
from pymongo import ReturnDocument
import discord as typehint_Discord
import logging
import motor.motor_asyncio
from datetime import datetime
import time
import re

_fetchdict = HelperFunctions.fetch_default_model(
    model_type="reasoning", output_modalities="text", provider="gemini"
)
DEFAULT_MODEL = f"{_fetchdict['provider']}::{_fetchdict['model_name']}"


# A class that is responsible for managing and manipulating the chat history
class History:
    def __init__(
        self,
        bot: typehint_Discord.Bot,
        db_conn: motor.motor_asyncio.AsyncIOMotorClient = None,
    ):
        self._db_conn = db_conn
        self._knowledge_indexes = set()

        if db_conn is None:
            raise ConnectionError("Please set MONGO_DB_URL in dev.env")

        # Create a new database if it doesn't exist, access chat_history database
        self._db = self._db_conn[environ.get("MONGO_DB_NAME", "jakey_prod_db")]
        self._collection = self._db[
            environ.get("MONGO_DB_COLLECTION_NAME", "jakey_prod_db_collection")
        ]
        logging.info(
            "Connected to the database %s and collection %s",
            self._db.name,
            self._collection.name,
        )

        # Create task for indexing the collection
        bot.loop.create_task(self._init_indexes())

    # Setup indexes for the collection
    async def _init_indexes(self):
        await self._collection.create_index(
            [("guild_id", 1)], name="guild_id_index", background=True, unique=True
        )
        logging.info("Created index for guild_id")

    # Type validation for guild_id
    def _normalize_guild_id(self, guild_id: int) -> str:
        if guild_id is None:
            raise TypeError("guild_id is required")
        _guild_id_str = str(guild_id)
        if not _guild_id_str.isdigit():
            raise ValueError("guild_id must be a string of digits")
        return _guild_id_str

    # Returns the document to be manipulated, creates one if it doesn't exist.
    async def _ensure_document(
        self, guild_id: str, model: str = DEFAULT_MODEL, tool_use: str = None
    ):
        # Use environment variable for default tool if not specified
        if tool_use is None:
            tool_use = environ.get("DEFAULT_TOOL", "Memory")
        # Check if guild_id is string
        if not isinstance(guild_id, str):
            raise TypeError("guild_id is required and must be a string")

        _existing = await self._collection.find_one({"guild_id": guild_id})
        if _existing:
            tool_use = _existing.get("tool_use", tool_use)
            default_model = _existing.get("default_model", model)
            default_openrouter_model = _existing.get(
                "default_openrouter_model", "openai/gpt-4.1-mini"
            )
        else:
            tool_use = tool_use
            default_model = model
            default_openrouter_model = "openai/gpt-4.1-mini"

        # Use find_one_and_update with upsert to return the document after update.
        _document = await self._collection.find_one_and_update(
            {"guild_id": guild_id},
            {
                "$set": {
                    "guild_id": guild_id,
                    "tool_use": tool_use,
                    "default_model": default_model,
                    "default_openrouter_model": default_openrouter_model,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return _document

    ####################################################################################
    # Chat History Management
    ####################################################################################

    # Load chat history
    async def load_history(self, guild_id: int, model_provider: str):
        guild_id = self._normalize_guild_id(guild_id)
        _document = await self._ensure_document(guild_id)

        # Check if model_provider_{model_provider} exists in the document
        if f"chat_thread_{model_provider}" not in _document:
            await self._collection.update_one(
                {"guild_id": guild_id},
                {"$set": {f"chat_thread_{model_provider}": None}},
            )
            _document[f"chat_thread_{model_provider}"] = None

        # Prepend current date and time to the chat history
        current_time_context = self._get_current_time_context()
        if _document[f"chat_thread_{model_provider}"]:
            return [current_time_context] + _document[f"chat_thread_{model_provider}"]
        else:
            return [current_time_context]

    async def save_history(
        self, guild_id: int, chat_thread, model_provider: str
    ) -> None:
        guild_id = self._normalize_guild_id(guild_id)
        await self._ensure_document(guild_id)
        await self._collection.update_one(
            {"guild_id": guild_id},
            {"$set": {f"chat_thread_{model_provider}": chat_thread}},
            upsert=True,
        )

    # Clear chat history
    async def clear_history(self, guild_id: int) -> None:
        guild_id = self._normalize_guild_id(guild_id)
        await self._collection.delete_one({"guild_id": guild_id})

    def _get_current_time_context(self) -> str:
        """Returns a formatted string with the current date, time, and DST status."""
        now = datetime.now()
        dst_status = "active" if time.localtime().tm_isdst else "inactive"
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}. Daylight Saving Time is currently {dst_status}."

    # Tool configuration management
    async def set_tool_config(self, guild_id: int, tool: str = None) -> None:
        guild_id = self._normalize_guild_id(guild_id)
        await self._ensure_document(guild_id, tool)
        await self._collection.update_one(
            {"guild_id": guild_id}, {"$set": {"tool_use": tool}}, upsert=True
        )

    async def get_tool_config(self, guild_id: int):
        guild_id = self._normalize_guild_id(guild_id)
        _document = await self._ensure_document(guild_id)
        return _document["tool_use"]

    # Default model management
    async def set_default_model(self, guild_id: int, model: str) -> None:
        guild_id = self._normalize_guild_id(guild_id)

        if not model or not isinstance(model, str):
            raise ValueError("Model must be a non-empty string")

        await self._ensure_document(guild_id, model=model)
        try:
            await self._collection.update_one(
                {"guild_id": guild_id}, {"$set": {"default_model": model}}, upsert=True
            )
        except Exception as e:
            logging.error("Error setting default model: %s", e)
            raise HistoryDatabaseError("Error setting default model")

    # Get default model
    async def get_default_model(self, guild_id: int):
        guild_id = self._normalize_guild_id(guild_id)
        try:
            _document = await self._ensure_document(guild_id)
            return _document["default_model"]
        except Exception as e:
            logging.error("Error getting default model: %s", e)
            raise HistoryDatabaseError("Error getting default model")

    # Directly set custom keys and values to the document
    async def set_key(self, guild_id: int, key: str, value) -> None:
        guild_id = self._normalize_guild_id(guild_id)
        await self._ensure_document(guild_id)
        try:
            await self._collection.update_one(
                {"guild_id": guild_id}, {"$set": {key: value}}, upsert=True
            )
        except Exception as e:
            logging.error("Error setting keys: %s", e)
            raise HistoryDatabaseError(f"Error setting keys: {key}")

    # Directly get custom keys and values from the document
    async def get_key(self, guild_id: int, key: str):
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")

        guild_id = self._normalize_guild_id(guild_id)
        _document = await self._ensure_document(guild_id)
        try:
            return _document[key]
        except Exception as e:
            logging.error("Error getting key: %s", e)
            raise HistoryDatabaseError(f"Error getting key: {key}")

    ####################################################################################
    # Knowledge Base Management
    ####################################################################################

    async def add_fact(
        self,
        guild_id: int,
        user_id: int,
        fact_text: str,
        source: str,
        expires_at: datetime = None,
    ):
        """Store a fact in the knowledge base with expiration"""
        guild_id = self._normalize_guild_id(guild_id)
        knowledge_collection = self._db[f"knowledge_{guild_id}"]

        fact = {
            "user_id": user_id,
            "fact_text": fact_text,
            "source": source,
            "created_at": datetime.utcnow(),
            "last_accessed_at": datetime.utcnow(),
            "relevance_score": 0,  # Default relevance score
            "expires_at": expires_at,
        }
        result = await knowledge_collection.insert_one(fact)
        return result.inserted_id

    async def add_reminder(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        message: str,
        remind_time: datetime,
    ):
        """Store a reminder in the database"""
        guild_id = self._normalize_guild_id(guild_id)
        reminders_collection = self._db[f"reminders_{guild_id}"]

        reminder = {
            "user_id": user_id,
            "channel_id": channel_id,
            "message": message,
            "remind_time": remind_time,
            "created_at": datetime.utcnow(),
        }
        result = await reminders_collection.insert_one(reminder)
        return result.inserted_id

    async def get_due_reminders(self, guild_id: int):
        """Retrieve reminders that are due from the database"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"reminders_{guild_id}"

        if collection_name not in await self._db.list_collection_names():
            return []

        reminders_collection = self._db[collection_name]
        now = datetime.utcnow()
        due_reminders = []
        async for reminder in reminders_collection.find({"remind_time": {"$lte": now}}):
            due_reminders.append(reminder)
        return due_reminders

    async def delete_reminder(self, guild_id: int, reminder_id):
        """Remove a reminder from the database"""
        guild_id = self._normalize_guild_id(guild_id)
        reminders_collection = self._db[f"reminders_{guild_id}"]
        await reminders_collection.delete_one({"_id": reminder_id})

    async def get_fact(self, guild_id: int, fact_id: str):
        """Retrieve a fact from the knowledge base if not expired"""
        guild_id = self._normalize_guild_id(guild_id)
        knowledge_collection = self._db[f"knowledge_{guild_id}"]
        fact = await knowledge_collection.find_one({"_id": fact_id})
        if fact and (
            fact["expires_at"] is None or fact["expires_at"] > datetime.utcnow()
        ):
            # Update last_accessed_at
            await knowledge_collection.update_one(
                {"_id": fact_id}, {"$set": {"last_accessed_at": datetime.utcnow()}}
            )
            return fact["fact_text"]
        return None

    async def search_facts(self, guild_id: int, query: str, limit: int = 5):
        """Search for relevant facts using multiple search strategies"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"knowledge_{guild_id}"

        if collection_name not in await self._db.list_collection_names():
            return []

        knowledge_collection = self._db[collection_name]
        results = []

        try:
            # First try: Text search with MongoDB text index
            if guild_id not in self._knowledge_indexes:
                try:
                    await knowledge_collection.create_index([("fact_text", "text")])
                    self._knowledge_indexes.add(guild_id)
                except Exception as e:
                    logging.warning(
                        f"Failed to create text index for guild {guild_id}: {e}"
                    )

            # Try text search first
            try:
                async for fact in knowledge_collection.find(
                    {"$text": {"$search": query}}
                ).limit(limit):
                    if fact and (
                        fact.get("expires_at") is None
                        or fact["expires_at"] > datetime.utcnow()
                    ):
                        results.append(fact["fact_text"])
            except Exception as e:
                logging.warning(f"Text search failed for guild {guild_id}: {e}")

            # If text search didn't return enough results, try regex search
            if len(results) < limit:
                try:
                    # Create a regex pattern for case-insensitive search
                    regex_pattern = re.compile(re.escape(query), re.IGNORECASE)

                    async for fact in knowledge_collection.find(
                        {"fact_text": {"$regex": regex_pattern}}
                    ).limit(limit - len(results)):
                        if fact and (
                            fact.get("expires_at") is None
                            or fact["expires_at"] > datetime.utcnow()
                        ):
                            fact_text = fact["fact_text"]
                            if fact_text not in results:  # Avoid duplicates
                                results.append(fact_text)
                except Exception as e:
                    logging.warning(f"Regex search failed for guild {guild_id}: {e}")

            # If still not enough results, try partial word matching
            if len(results) < limit:
                try:
                    words = query.lower().split()
                    for word in words:
                        if (
                            len(word) > 2
                        ):  # Only search for words longer than 2 characters
                            word_pattern = re.compile(re.escape(word), re.IGNORECASE)

                            async for fact in knowledge_collection.find(
                                {"fact_text": {"$regex": word_pattern}}
                            ).limit(limit - len(results)):
                                if fact and (
                                    fact.get("expires_at") is None
                                    or fact["expires_at"] > datetime.utcnow()
                                ):
                                    fact_text = fact["fact_text"]
                                    if fact_text not in results:  # Avoid duplicates
                                        results.append(fact_text)
                                        if len(results) >= limit:
                                            break
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logging.warning(
                        f"Partial word search failed for guild {guild_id}: {e}"
                    )

        except Exception as e:
            logging.error(f"Search failed for guild {guild_id}: {e}")

        return results[:limit]

    async def get_facts_by_user(self, guild_id: int, user_id: int, limit: int = 10):
        """Get facts stored by a specific user"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"knowledge_{guild_id}"

        if collection_name not in await self._db.list_collection_names():
            return []

        knowledge_collection = self._db[collection_name]
        facts = []

        try:
            async for fact in knowledge_collection.find({"user_id": user_id}).limit(
                limit
            ):
                if fact and (
                    fact.get("expires_at") is None
                    or fact["expires_at"] > datetime.utcnow()
                ):
                    facts.append(fact["fact_text"])
        except Exception as e:
            logging.error(f"Failed to get facts by user for guild {guild_id}: {e}")

        return facts

    async def get_recent_facts(self, guild_id: int, limit: int = 10):
        """Get recently accessed facts"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"knowledge_{guild_id}"

        if collection_name not in await self._db.list_collection_names():
            return []

        knowledge_collection = self._db[collection_name]
        facts = []

        try:
            async for fact in (
                knowledge_collection.find().sort("last_accessed_at", -1).limit(limit)
            ):
                if fact and (
                    fact.get("expires_at") is None
                    or fact["expires_at"] > datetime.utcnow()
                ):
                    facts.append(fact["fact_text"])
        except Exception as e:
            logging.error(f"Failed to get recent facts for guild {guild_id}: {e}")

        return facts

    async def check_memory_status(self, guild_id: int):
        """Check the status of the memory system for debugging"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"knowledge_{guild_id}"

        try:
            # Check if collection exists
            collections = await self._db.list_collection_names()
            collection_exists = collection_name in collections

            if not collection_exists:
                return {
                    "status": "no_collection",
                    "message": f"Knowledge collection '{collection_name}' does not exist",
                    "total_facts": 0,
                    "collections": collections,
                }

            knowledge_collection = self._db[collection_name]

            # Count total facts
            total_facts = await knowledge_collection.count_documents({})

            # Count non-expired facts
            now = datetime.utcnow()
            non_expired_facts = await knowledge_collection.count_documents(
                {
                    "$or": [
                        {"expires_at": {"$exists": False}},
                        {"expires_at": None},
                        {"expires_at": {"$gt": now}},
                    ]
                }
            )

            # Check for text index
            indexes = await knowledge_collection.list_indexes().to_list(None)
            text_index_exists = any(
                index.get("key", {}).get("fact_text") == "text" for index in indexes
            )

            return {
                "status": "ok",
                "message": "Memory system is operational",
                "total_facts": total_facts,
                "non_expired_facts": non_expired_facts,
                "text_index_exists": text_index_exists,
                "collection_name": collection_name,
                "indexes": [index.get("name") for index in indexes],
            }

        except Exception as e:
            logging.error(f"Failed to check memory status for guild {guild_id}: {e}")
            return {
                "status": "error",
                "message": f"Error checking memory status: {str(e)}",
                "total_facts": 0,
                "non_expired_facts": 0,
                "text_index_exists": False,
            }

    async def force_reindex_memory(self, guild_id: int):
        """Force reindex the memory collection to fix search issues"""
        guild_id = self._normalize_guild_id(guild_id)
        collection_name = f"knowledge_{guild_id}"

        try:
            knowledge_collection = self._db[collection_name]

            # Drop existing text index if it exists
            try:
                await knowledge_collection.drop_index("fact_text_text")
                logging.info(f"Dropped existing text index for {collection_name}")
            except Exception as e:
                logging.info(
                    f"No existing text index to drop for {collection_name}: {e}"
                )

            # Create new text index
            await knowledge_collection.create_index([("fact_text", "text")])
            logging.info(f"Created new text index for {collection_name}")

            # Reset the knowledge indexes set
            if guild_id in self._knowledge_indexes:
                self._knowledge_indexes.remove(guild_id)

            return True

        except Exception as e:
            logging.error(f"Failed to reindex memory for guild {guild_id}: {e}")
            return False

    async def delete_fact(self, guild_id: int, fact_id: str):
        """Remove a fact from the knowledge base"""
        guild_id = self._normalize_guild_id(guild_id)
        knowledge_collection = self._db[f"knowledge_{guild_id}"]
        await knowledge_collection.delete_one({"_id": fact_id})

    ####################################################################################
    # Trivia Score Management
    ####################################################################################

    async def add_trivia_score(self, guild_id: int, user_id: int, score: int):
        """Add or update a user's trivia score for a guild."""
        guild_id = self._normalize_guild_id(guild_id)
        trivia_scores_collection = self._db[f"trivia_scores_{guild_id}"]

        await trivia_scores_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"score": score}, "$set": {"last_updated": datetime.utcnow()}},
            upsert=True
        )
        logging.info(f"User {user_id} in guild {guild_id} scored {score} trivia points.")

    async def get_trivia_leaderboard(self, guild_id: int, limit: int = 10):
        """Retrieve the top trivia scores for a guild."""
        guild_id = self._normalize_guild_id(guild_id)
        trivia_scores_collection = self._db[f"trivia_scores_{guild_id}"]

        leaderboard = []
        async for entry in trivia_scores_collection.find().sort("score", -1).limit(limit):
            leaderboard.append(entry)
        return leaderboard
