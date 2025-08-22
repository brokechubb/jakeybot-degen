from tools.Memory.manifest import ToolManifest
from core.ai.history import History
from datetime import datetime, timedelta
import logging
import re


class Tool(ToolManifest):
    # Required attributes for bot system recognition
    tool_human_name = "Memory Recall"

    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot
        self.history_db = None

        # Set the schema attributes for this instance
        self.tool_schema = self.tool_schema_basic
        self.tool_schema_openai = self.tool_schema_openai

        # Initialize history database connection
        try:
            from core.services.helperfunctions import HelperFunctions
            from motor.motor_asyncio import AsyncIOMotorClient
            from os import environ

            db_conn = AsyncIOMotorClient(environ.get("MONGO_DB_URL"))
            self.history_db = History(bot=discord_bot, db_conn=db_conn)
        except Exception as e:
            logging.error(f"Failed to initialize Memory tool database connection: {e}")
            self.history_db = None

    async def _tool_function_remember_fact(
        self, fact: str, category: str = None, expires_in: str = None
    ):
        """Store a new fact in memory"""
        if not self.history_db:
            return "❌ Memory system is not available at the moment"

        try:
            # Determine guild/user ID
            guild_id = (
                self.discord_ctx.guild.id
                if self.discord_ctx.guild
                else self.discord_ctx.author.id
            )
            user_id = self.discord_ctx.author.id

            # Parse expiration time
            expires_at = None
            if expires_in and expires_in.lower() != "never":
                try:
                    now = datetime.utcnow()
                    if expires_in.endswith("d"):
                        days = int(expires_in[:-1])
                        expires_at = now + timedelta(days=days)
                    elif expires_in.endswith("h"):
                        hours = int(expires_in[:-1])
                        expires_at = now + timedelta(hours=hours)
                    elif expires_in.endswith("m"):
                        minutes = int(expires_in[:-1])
                        expires_at = now + timedelta(minutes=minutes)
                    else:
                        raise ValueError("Invalid time format")
                except:
                    return "⚠️ Invalid expiration format. Use number followed by d, h, or m (e.g., 1d, 2h, 30m), or 'never' for permanent"

            # Add category to fact text if provided
            if category:
                fact_with_category = f"[{category}] {fact}"
            else:
                fact_with_category = fact

            # Store the fact
            fact_id = await self.history_db.add_fact(
                guild_id=guild_id,
                user_id=user_id,
                fact_text=fact_with_category,
                source=f"memory_tool/{user_id}",
                expires_at=expires_at,
            )

            response = f"✅ I'll remember that: **{fact}**"
            if category:
                response += f" (Category: {category})"
            if expires_at:
                response += f"\n⏰ Expires: {expires_at.strftime('%Y-%m-%d %H:%M')} UTC"
            else:
                response += " (Permanent)"

            # Return a natural response that the AI can use
            return f"I've remembered that {fact}. This information is now stored in my memory for future conversations."

        except Exception as e:
            logging.error(f"Error storing fact: {e}")
            return f"❌ Failed to store fact: {str(e)}"

    async def _tool_function_recall_fact(self, query: str, limit: int = 3):
        """Search for and retrieve relevant facts from memory"""
        if not self.history_db:
            return "❌ Memory system is not available at the moment"

        try:
            # Determine guild/user ID
            guild_id = (
                self.discord_ctx.guild.id
                if self.discord_ctx.guild
                else self.discord_ctx.author.id
            )

            # Limit the search results
            limit = min(max(1, limit), 10)

            # Search for facts
            facts = await self.history_db.search_facts(guild_id, query, limit=limit)

            if not facts:
                return f"🤔 I couldn't find any facts matching '{query}' in my memory"

            # Format the response
            if len(facts) == 1:
                response = f"📝 Here's what I remember about '{query}':\n**{facts[0]}**"
            else:
                response = f"📝 Here are the facts I found about '{query}':\n"
                for i, fact in enumerate(facts, 1):
                    response += f"{i}. **{fact}**\n"

            # Return the facts in a natural format for the AI to use
            if len(facts) == 1:
                return f"I found this information in my memory: {facts[0]}"
            else:
                facts_text = "; ".join(facts)
                return f"I found these details in my memory: {facts_text}"

        except Exception as e:
            logging.error(f"Error recalling facts: {e}")
            return f"❌ Failed to recall facts: {str(e)}"

    async def _tool_function_list_facts(self, category: str = None, limit: int = 10):
        """List all facts in a specific category or all facts"""
        if not self.history_db:
            return "❌ Memory system is not available at the moment"

        try:
            # Determine guild/user ID
            guild_id = (
                self.discord_ctx.guild.id
                if self.discord_ctx.guild
                else self.discord_ctx.author.id
            )

            # Limit the results
            limit = min(max(1, limit), 20)

            # Get facts from the knowledge base
            knowledge_collection = self.history_db._db[f"knowledge_{guild_id}"]

            # Build query
            query = {}
            if category:
                query["fact_text"] = {
                    "$regex": f"^\\[{re.escape(category)}\\]",
                    "$options": "i",
                }

            # Get facts
            facts = []
            async for fact in knowledge_collection.find(query).limit(limit):
                if fact and (
                    fact.get("expires_at") is None
                    or fact["expires_at"] > datetime.utcnow()
                ):
                    facts.append(fact["fact_text"])

            if not facts:
                if category:
                    return f"🤔 I don't have any facts in the '{category}' category"
                else:
                    return "🤔 I don't have any facts stored in my memory yet"

            # Format the response
            if category:
                response = f"📋 Facts in category '{category}':\n"
            else:
                response = f"📋 All facts in my memory:\n"

            for i, fact in enumerate(facts, 1):
                response += f"{i}. {fact}\n"

            if len(facts) == limit:
                response += f"\n... and more (showing first {limit})"

            # Return the facts in a natural format for the AI to use
            if len(facts) == 1:
                return f"I have one fact stored: {facts[0]}"
            else:
                facts_text = "; ".join(facts)
                return f"I have {len(facts)} facts stored: {facts_text}"

        except Exception as e:
            logging.error(f"Error listing facts: {e}")
            return f"❌ Failed to list facts: {str(e)}"
