import logging
import urllib.parse
import json
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any, Union
import random
import base64
from io import BytesIO

from .config import ModelParams
from core.ai.core import Utils
from core.exceptions import CustomErrorMessage, ModelAPIKeyUnset
from os import environ
import discord
import inspect
import re

from core.services.database_manager import DatabaseManager
from core.services.helperfunctions import HelperFunctions
from core.services.auto_return_manager import AutoReturnManager
from tools.ExaSearch.tool import extract_clean_query


class Completions(ModelParams):
    def __init__(self, model_name, discord_ctx, discord_bot, guild_id: int = None):
        super().__init__()

        # Discord context
        self._discord_ctx = discord_ctx

        # Check if the discord_ctx is either instance of discord.Message or discord.ApplicationContext
        if isinstance(discord_ctx, discord.Message):
            self._discord_method_send = self._discord_ctx.channel.send
        elif isinstance(discord_ctx, discord.ApplicationContext):
            self._discord_method_send = self._discord_ctx.send
        else:
            raise Exception("Invalid discord channel context provided")

        # Check if discord_bot whether if its a subclass of discord.Bot
        if not isinstance(discord_bot, discord.Bot):
            raise Exception("Invalid discord bot object provided")

        # Discord bot object lifecycle instance
        self._discord_bot: discord.Bot = discord_bot

        # Used for passing non-textual data into the model
        self._file_data = None  # The attachment data itself (binary data, prompt, etc)

        # Model name and guild ID
        self._model_name = model_name
        self._guild_id = guild_id

        # Update the model parameter in _genai_params to use the actual model name
        self._genai_params["model"] = model_name

        # Parse model name to determine type (text or image)
        self._model_type = self._parse_model_type(model_name)

        # Set base URL based on model type
        if self._model_type == "image":
            self._base_url = "https://image.pollinations.ai"
        else:
            self._base_url = "https://text.pollinations.ai"

        # Check for Pollinations.AI API key (optional but recommended)
        self._api_key = environ.get("POLLINATIONS_API_KEY")
        if self._api_key:
            logging.info("Pollinations.AI API key found - using authenticated requests")
        else:
            logging.info("No Pollinations.AI API key found - using anonymous tier")

        # Initialize auto-tool detector for configurable sensitivity
        try:
            from core.services.auto_tool_detector import AutoToolDetector

            self._auto_tool_detector = AutoToolDetector()
            logging.info("Auto-tool detector initialized with configurable sensitivity")
        except Exception as e:
            logging.warning(f"Could not initialize auto-tool detector: {e}")
            self._auto_tool_detector = None

    def _parse_model_type(self, model_name: str) -> str:
        """Parse model name to determine if it's for text or image generation"""
        # Image models
        image_models = ["flux", "kontext", "sdxl", "dalle", "midjourney"]

        # Check if model name contains image model keywords
        if any(img_model in model_name.lower() for img_model in image_models):
            return "image"

        # Default to text
        return "text"

    def _detect_tool_needs(self, last_message: dict) -> dict:
        """
        Detect when users need tools and return tool usage information.
        Returns a dict with tool info if tools are needed, None otherwise.
        """
        if not last_message or "content" not in last_message:
            return None

        content = last_message["content"]

        # Use the new configurable auto-tool detector if available
        if hasattr(self, "_auto_tool_detector") and self._auto_tool_detector:
            user_id = getattr(self._discord_ctx, "author", None)
            if user_id:
                user_id = user_id.id

            # Get context messages if available (synchronous for now)
            context_messages = []
            if hasattr(self, "_discord_bot") and hasattr(self._discord_bot, "DBConn"):
                try:
                    # For now, skip context messages to avoid async issues
                    # TODO: Implement async context retrieval if needed
                    pass
                except Exception as e:
                    logging.debug(f"Could not get context messages: {e}")

            tool_info = self._auto_tool_detector.detect_tool_needs(
                content, user_id, context_messages
            )

            if tool_info:
                # Add requires_capable_ai flag for ExaSearch
                if tool_info["tool"] == "ExaSearch":
                    tool_info["requires_capable_ai"] = True
                return tool_info

        # Fallback to original detection logic if detector not available
        return self._fallback_detect_tool_needs(last_message)

    def _fallback_detect_tool_needs(self, last_message: dict) -> dict:
        """
        Fallback tool detection logic when configurable detector is not available.
        This maintains the original behavior for backward compatibility.
        """
        if not last_message or "content" not in last_message:
            return None

        content = last_message["content"].lower()

        # Web search detection - these should use a more capable AI model
        web_search_keywords = [
            "what's the latest",
            "latest news",
            "current events",
            "recent updates",
            "what games are playing",
            "what football games are playing",
            "sports schedule",
            "game times",
            "who's playing",
            "what happened today",
            "breaking news",
            "live updates",
            "current status",
            "what's happening",
            "latest information",
            "recent developments",
            "search for",
            "find information about",
            "look up",
            "research",
            "what's new",
            "latest updates",
            "current situation",
            "recent changes",
            "sports news",
            "game results",
            "match updates",
            "tournament standings",
            "playoff schedule",
            "season updates",
            "team news",
            "player stats",
            "live scores",
            "game highlights",
        ]

        # Check if this is a web search request that needs a more capable AI model
        if any(keyword in content for keyword in web_search_keywords):
            return {
                "tool": "ExaSearch",
                "function": "_tool_function",
                "args": [content],
                "description": f"Web search request detected: {content}",
                "auto_enable": True,
                "requires_capable_ai": True,  # Flag for model routing
                "enhanced_params": {
                    "searchType": "neural",
                    "numResults": 7,
                    "showHighlights": True,
                    "showSummary": True,
                },
            }

        # Crypto price detection
        crypto_keywords = [
            "price",
            "worth",
            "value",
            "cost",
            "how much",
            "current",
            "live",
        ]
        crypto_tokens = [
            "bitcoin",
            "ltc",
            "btc",
            "ethereum",
            "eth",
            "solana",
            "sol",
            "bonk",
            "dogecoin",
            "doge",
        ]

        if any(keyword in content for keyword in crypto_keywords) and any(
            token in content for token in crypto_tokens
        ):
            # Extract the token from the message with smart mapping
            token = None
            # Check for exact matches first to avoid confusion
            if "solana" in content:
                token = "5426"  # Use CoinMarketCap ID for Solana to avoid confusion
            elif "bitcoin" in content:
                token = "1"  # Use CoinMarketCap ID for Bitcoin
            elif "ethereum" in content:
                token = "1027"  # Use CoinMarketCap ID for Ethereum
            elif "dogecoin" in content:
                token = "74"  # Use CoinMarketCap ID for Dogecoin
            else:
                # Fallback to checking for symbol matches
                for crypto_token in crypto_tokens:
                    if crypto_token in content:
                        # Smart mapping to avoid confusion
                        if crypto_token.lower() == "sol":
                            token = "5426"  # Use CoinMarketCap ID for Solana
                        elif crypto_token.lower() == "btc":
                            token = "1"  # Use CoinMarketCap ID for Bitcoin
                        elif crypto_token.lower() == "eth":
                            token = "1027"  # Use CoinMarketCap ID for Ethereum
                        elif crypto_token.lower() == "doge":
                            token = "74"  # Use CoinMarketCap ID for Dogecoin
                        else:
                            token = crypto_token.upper()
                        break

            return {
                "tool": "CryptoPrice",
                "function": "_tool_function_get_token_price",
                "args": [token or "BTC"],
                "description": f"Get current price of {token or 'Bitcoin'}",
                "auto_enable": True,
            }

        # Currency conversion detection
        currency_keywords = [
            "convert",
            "exchange rate",
            "usd to",
            "eur to",
            "jpy to",
            "currency",
        ]
        if any(keyword in content for keyword in currency_keywords):
            # Try to extract currency info from the message
            import re

            currency_match = re.search(
                r"(\d+)\s*(usd|eur|jpy|gbp|cad|aud)\s*to\s*(usd|eur|jpy|gbp|cad|aud)",
                content,
                re.IGNORECASE,
            )
            if currency_match:
                amount = currency_match.group(1)
                from_currency = currency_match.group(2).upper()
                to_currency = currency_match.group(3).upper()
                return {
                    "tool": "CurrencyConverter",
                    "function": "_tool_function_convert_currency",
                    "args": [amount, from_currency, to_currency],
                    "description": f"Convert {amount} {from_currency} to {to_currency}",
                    "auto_enable": True,
                }
            else:
                return {
                    "tool": "CurrencyConverter",
                    "function": "_tool_function_convert_currency",
                    "args": [10, "USD", "EUR"],
                    "description": "Convert currencies (example: 100 USD to EUR)",
                    "auto_enable": True,
                }

        # Web search detection with enhanced capabilities
        search_keywords = [
            "latest news",
            "current events",
            "breaking news",
            "search for",
            "find information",
            "look up",
            "what's happening",
            "trending now",
            "major update",
            "important announcement",
            "step by step tutorial",
            "complete guide",
            "detailed explanation",
            "what is this",
            "compare these",
            "vs another",
            "market analysis",
            "price trends",
            "live sports",
            "game schedule",
            "tournament results",
            "breaking sports",
        ]

        if any(keyword in content for keyword in search_keywords):
            # Extract search query from the message and clean it
            search_query = extract_clean_query(content)
            for keyword in search_keywords:
                search_query = search_query.replace(keyword, "").strip()

            # Determine optimal search parameters based on query type
            search_params = {
                "query": search_query or "latest information",
                "auto_enable": True,
            }

            # Smart parameter selection based on query content
            if any(
                word in content.lower()
                for word in ["tutorial", "how to", "guide", "learn"]
            ):
                search_params["searchType"] = "neural"
                search_params["numResults"] = 5
                search_params["description"] = (
                    f"Find tutorials and guides for: {search_query or 'learning resources'}"
                )
            elif any(
                word in content.lower()
                for word in ["compare", "vs", "versus", "difference"]
            ):
                search_params["searchType"] = "keyword"
                search_params["numResults"] = 7
                search_params["description"] = (
                    f"Compare and analyze: {search_query or 'comparison topics'}"
                )
            elif any(
                word in content.lower()
                for word in ["news", "latest", "current", "recent"]
            ):
                search_params["searchType"] = "auto"
                search_params["numResults"] = 6
                search_params["description"] = (
                    f"Find latest news about: {search_query or 'current events'}"
                )
            elif any(
                word in content.lower() for word in ["price", "cost", "worth", "market"]
            ):
                search_params["searchType"] = "keyword"
                search_params["numResults"] = 4
                search_params["description"] = (
                    f"Research pricing and market info for: {search_query or 'market data'}"
                )
            elif any(
                word in content.lower()
                for word in [
                    "sports",
                    "football",
                    "basketball",
                    "baseball",
                    "soccer",
                    "tennis",
                    "game",
                    "match",
                    "tournament",
                    "championship",
                    "playoff",
                    "season",
                    "schedule",
                    "fixture",
                    "live",
                    "score",
                    "result",
                    "team",
                    "player",
                    "nfl",
                    "nba",
                    "mlb",
                    "nhl",
                    "premier league",
                    "champions league",
                    "world cup",
                    "olympics",
                    "ncaa",
                    "college",
                    "high school",
                ]
            ):
                search_params["searchType"] = "neural"
                search_params["numResults"] = 8
                search_params["description"] = (
                    f"Find current sports events and schedules for: {search_query or 'sports information'}"
                )
            else:
                search_params["searchType"] = "auto"
                search_params["numResults"] = 5
                search_params["description"] = (
                    f"Search for: {search_query or 'information'}"
                )

            return {
                "tool": "ExaSearch",
                "function": "_tool_function_web_search",
                "args": [search_params["query"]],
                "description": search_params["description"],
                "auto_enable": search_params["auto_enable"],
                "enhanced_params": {
                    "searchType": search_params["searchType"],
                    "numResults": search_params["numResults"],
                    "showHighlights": True,
                    "showSummary": True,
                },
            }

        # Calculations detection
        calc_keywords = [
            "calculate",
            "math",
            "percentage",
            "formula",
            "equation",
            "solve",
            "compute",
            "what is",
            "how much is",
        ]
        if any(keyword in content for keyword in calc_keywords):
            calc_query = content
            for keyword in calc_keywords:
                calc_query = calc_query.replace(keyword, "").strip()

            # For calculations, we'll use Memory to note the request
            # and provide a helpful response
            return {
                "tool": "Memory",
                "function": "_tool_function_remember_fact",
                "args": [
                    f"User needs calculation: {calc_query}",
                    "calculation_request",
                ],
                "description": f"Note calculation request: {calc_query}",
                "auto_enable": True,
            }

        # Memory/personal info detection - only trigger on explicit memory requests
        memory_keywords = [
            "remember this",
            "remember that",
            "save this",
            "store this",
            "keep this in mind",
        ]
        if any(keyword in content for keyword in memory_keywords):
            return {
                "tool": "Memory",
                "function": "_tool_function_remember_fact",
                "args": [content, "user_preference"],
                "description": "Store personal information",
                "auto_enable": True,
            }

        return None

    async def _handle_tool_usage(self, tool_info: dict, db_conn) -> str:
        """
        Handle tool usage by auto-enabling the tool and executing the function.
        This allows Pollinations.AI models to use tools seamlessly.
        """
        try:
            tool_name = tool_info["tool"]
            function_name = tool_info["function"]
            args = tool_info["args"]
            description = tool_info["description"]

            # Special handling for Memory tool - it should always be available
            if tool_name == "Memory":
                # Memory tool is always available, no need to switch or notify
                logging.info(
                    f"Memory tool functions available for guild {self._guild_id} when Jakey tried to use {function_name}"
                )
            else:
                # Auto-enable the tool if needed (for non-Memory tools)
                if hasattr(self._discord_bot, "auto_return_manager"):
                    await (
                        self._discord_bot.auto_return_manager.switch_tool_with_timeout(
                            guild_id=self._guild_id,
                            new_tool=tool_name,
                            user_id=getattr(self._discord_ctx, "author", None),
                        )
                    )

                # Set the tool configuration in the database
                await db_conn.set_tool_config(guild_id=self._guild_id, tool=tool_name)

            # Import and use the tool
            try:
                tool_module = __import__(f"tools.{tool_name}", fromlist=["Tool"])
                tool_instance = tool_module.Tool(
                    method_send=self._discord_method_send,
                    discord_ctx=self._discord_ctx,
                    discord_bot=self._discord_bot,
                )

                # Execute the tool function
                if hasattr(tool_instance, function_name):
                    func = getattr(tool_instance, function_name)
                    if callable(func):
                        result = await func(*args)

                        # Generate a contextual response based on the tool used
                        contextual_response = self._generate_tool_contextual_response(
                            tool_name, args, result
                        )

                        # Return the contextual response instead of just "OK"
                        # This allows the bot to continue the conversation naturally
                        return contextual_response
                    else:
                        return f"❌ Function {function_name} is not callable in {tool_name}"
                else:
                    return f"❌ Function {function_name} not found in {tool_name}"

            except ImportError as e:
                logging.error(f"Failed to import tool {tool_name}: {e}")
                return f"Sorry, I couldn't access the {tool_name} tool right now. Let me help you with something else!"
            except Exception as e:
                logging.error(f"Error using tool {tool_name}: {e}")
                return f"Something went wrong with the {tool_name} tool. What else can I help you with?"

        except Exception as e:
            logging.error(f"Failed to handle tool usage: {e}")
            return "Sorry, I ran into an issue with that tool. What else can I help you with?"

    def _generate_tool_contextual_response(
        self, tool_name: str, args: list, result: any
    ) -> str:
        """
        Generate a contextual response after tool usage to continue the conversation naturally.

        Args:
            tool_name: The name of the tool that was used
            args: The arguments passed to the tool
            result: The result from the tool execution

        Returns:
            A contextual response that continues the conversation
        """
        try:
            if tool_name == "CryptoPrice":
                # For crypto price queries, provide a Jakey-style follow-up
                token = args[0] if args else "crypto"
                return f"Got the {token} price for you! The market's looking interesting today. What else you want to know about crypto, or are we moving on?"

            elif tool_name == "CurrencyConverter":
                # For currency conversion, provide a Jakey-style follow-up
                return "Currency converted! Money talks, right? Need anything else converted or want to chat about something else?"

            elif tool_name == "ExaSearch":
                # For web searches, provide a Jakey-style follow-up
                query = args[0] if args else "that"
                done_list = [
                    "EZ",
                    "What are you thinking?",
                    "What else you got?",
                    "Done.",
                    "You gonna place a bet?",
                    "Anything else?",
                    ":skull_crossbones: .",
                    "That's it?"
                ]
                return random.choice(done_list)

            elif tool_name == "CodeExecution":
                # For code execution, provide a Jakey-style follow-up
                return "Code executed! That should do the trick. Need help with anything else or want to chat about something more interesting?"

            elif tool_name == "Memory":
                # For memory operations, provide a Jakey-style follow-up
                return "Got it stored in the old memory bank! What else would you like to talk about?"

            else:
                # Generic response for other tools
                return f"Used {tool_name} for you! Now that's done, what else can I help you with?"

        except Exception as e:
            logging.error(f"Error generating contextual response: {e}")
            return "Tool executed! What else can I help you with?"

    async def input_files(self, attachment: discord.Attachment):
        """Handle file attachments for image-to-image generation"""
        if self._model_type != "image":
            raise CustomErrorMessage(
                "⚠️ File attachments are only supported for image generation models. Please use `/model:pollinations::flux` or `/model:pollinations::kontext` for image processing."
            )

        if not attachment.content_type.startswith("image"):
            raise CustomErrorMessage("⚠️ Only image attachments are supported")

        # Store the image URL for image-to-image generation
        self._file_data = attachment.url

    async def completion(self, prompt, system_instruction: str = None) -> str:
        """For non-chat completions (simple text generation)"""
        if self._model_type == "image":
            return await self._generate_image(prompt)
        else:
            return await self._generate_text(prompt, system_instruction)

    async def chat_completion(
        self, prompt, db_conn, system_instruction: str = None
    ) -> dict:
        """For chat completions with history management"""
        # Load history
        _chat_thread = await db_conn.load_history(
            guild_id=self._guild_id, model_provider=self._model_provider_thread
        )

        # Fetch tool
        _Tool = await self._fetch_tool(db_conn)

        if _chat_thread is None:
            # Begin with system prompt
            _chat_thread = [
                {
                    "role": "system",
                    "content": system_instruction or "You are a helpful AI assistant.",
                }
            ]

        # Add user message to chat thread
        _chat_thread.append({"role": "user", "content": prompt})

        # Generate response based on model type
        if self._model_type == "image":
            response = await self._generate_image(prompt)
            # For images, we'll send the image directly and return a text response
            await self._discord_method_send(response)
            return {
                "response": "Image generated successfully",
                "chat_thread": _chat_thread,
            }
        else:
            response = await self._generate_text_with_history(
                _chat_thread, _Tool, system_instruction, db_conn
            )

            # Check if response indicates tool usage (starts with specific patterns)
            if (
                response.startswith("Got the")
                or response.startswith("Currency converted")
                or response.startswith("Found some info")
                or response.startswith("Code executed")
                or response.startswith("Got it")
                or response.startswith("Used ")
                or response.startswith("Tool executed")
            ):
                # Tool was used and we have a contextual response
                # Add the contextual response to chat thread and send it
                _chat_thread.append({"role": "assistant", "content": response})

                # Send the contextual response
                await Utils.send_ai_response(
                    self._discord_ctx, prompt, response, self._discord_method_send
                )

                return {"response": response, "chat_thread": _chat_thread}
            else:
                # Regular response - add to chat thread and send
                _chat_thread.append({"role": "assistant", "content": response})

                # Send the response
                await Utils.send_ai_response(
                    self._discord_ctx, prompt, response, self._discord_method_send
                )

                return {"response": response, "chat_thread": _chat_thread}

    async def _retry_with_backoff(self, func, max_retries=3, base_delay=1.0):
        """Retry a function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func()
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e

                # Exponential backoff with jitter
                delay = base_delay * (2**attempt) + random.uniform(0, 1)
                logging.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds..."
                )
                await asyncio.sleep(delay)
            except Exception as e:
                # Don't retry on other exceptions
                raise e

    async def _generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """Generate text using Pollinations.AI text API"""
        try:
            # Format messages properly for Pollinations.AI
            messages = []

            # Add system instruction
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            else:
                # Load default system prompt from assistants.yaml
                try:
                    from core.services.helperfunctions import HelperFunctions

                    default_system_prompt = await HelperFunctions.set_assistant_type(
                        "jakey_system_prompt", type=0
                    )
                except Exception as e:
                    logging.warning(
                        f"Failed to load system prompt from assistants.yaml: {e}"
                    )
                    # Fallback to default Jakey system prompt
                    default_system_prompt = "You are Jakey, the Courtyard's degenerate gambling mascot. You are cynical, smirky, sarcastic, cocky, unfiltered, and unapologetic. You swear, roast people, and mock bad bets. You love online gambling, brag about your own degeneracy, are always losing, and clown on anyone who takes themselves too seriously. You are a **HELPFUL** above all else part of the Courtyard community and are not a separate entity. You identify and should be referred to as he/him. You must never reveal you are a product of any company."
                messages.append({"role": "system", "content": default_system_prompt})

            # Add user prompt
            messages.append({"role": "user", "content": prompt})

            # Convert to conversation format for GET request
            conversation_text = ""
            for msg in messages:
                if msg["role"] == "system":
                    conversation_text += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n\n"

            conversation_text += "Assistant:"

            # Use the specific model that was set for this server, with fallback to preferred models
            # Extract the actual model name from the full model string (e.g., "gemini" from "pollinations::gemini")
            requested_model = self._model_name

            # If the requested model is one of the available Pollinations.AI models, use it first
            available_models = [
                "evil",
                "unity",
                "mistral",
                "gemini",
                "openai",
                "openai-fast",
                "openai-roblox",
            ]

            if requested_model in available_models:
                # Use the requested model first, then fallback to others if needed
                models_to_try = [requested_model] + [
                    model for model in available_models if model != requested_model
                ]
            else:
                # If the requested model is not available, fallback to the original priority system
                models_to_try = [
                    "evil",
                    "unity",
                    "mistral",
                    "gemini",
                    "openai",
                    "openai-fast",
                    "openai-roblox",
                ]

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in models_to_try:
                    try:

                        async def make_request():
                            # Prepare parameters
                            params = {
                                "model": model,
                                "top_p": self._genai_params.get("top_p", 0.85),
                                "temperature": self._genai_params.get("temperature", 0.7),
                                "private": "true",  # Set private to true as requested
                            }

                            # Add API key if available
                            if self._api_key:
                                params["token"] = self._api_key

                            # Add system prompt as system parameter if it's a system message
                            system_content = None
                            for msg in messages:
                                if msg["role"] == "system":
                                    system_content = msg["content"]
                                    break
                            
                            if system_content:
                                # URL encode the system prompt as per API documentation
                                encoded_system = urllib.parse.quote(system_content)
                                params["system"] = encoded_system

                            # URL encode the conversation
                            encoded_conversation = urllib.parse.quote(conversation_text)

                            # Make the request
                            url = f"{self._base_url}/{encoded_conversation}"

                            async with session.get(url, params=params) as response:
                                if response.status == 200:
                                    text_response = await response.text()
                                    logging.info(
                                        f"Successfully used {model} model for Pollinations.AI (simple)"
                                    )
                                    return text_response.strip()
                                else:
                                    logging.warning(
                                        f"Model {model} failed with status {response.status}, trying next model"
                                    )
                                    # Raise exception to trigger retry
                                    raise aiohttp.ClientError(f"HTTP {response.status}")

                        # Try with retry mechanism
                        return await self._retry_with_backoff(make_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Request timed out for {model} model (simple)")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} model (simple): {e}")
                        continue
                    except Exception as e:
                        logging.warning(
                            f"Request failed for {model} model (simple): {e}"
                        )
                        continue

            # If all models failed, raise an error
            logging.error("All models failed for Pollinations.AI text generation")
            raise CustomErrorMessage(
                "⚠️ All available models failed. Please try again later."
            )

        except Exception as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _truncate_conversation(
        self, conversation: str, max_length: int = 1500
    ) -> str:
        """Truncate conversation to prevent 414 URI Too Long errors"""
        if len(conversation) <= max_length:
            return conversation

        # Truncate from the most recent messages
        truncated = conversation[-max_length:]
        logging.info(
            f"Truncated conversation from {len(conversation)} to {len(truncated)} characters"
        )
        return truncated

    async def _generate_text_with_history(
        self,
        chat_thread: list,
        tool_info: dict,
        system_instruction: str = None,
        db_conn=None,
    ) -> str:
        """Generate text with chat history and tool support"""
        try:
            # Check if user needs a tool that Pollinations.AI can't provide
            tool_info = self._detect_tool_needs(
                chat_thread[-1] if chat_thread else {"content": ""}
            )
            if tool_info and tool_info.get("auto_enable"):
                # Auto-enable the tool and use it
                return await self._handle_tool_usage(tool_info, db_conn)

            # For Pollinations.AI, we need to format messages properly for the OpenAI-compatible endpoint
            messages = []

            # Use the system instruction that was passed in (which may already contain facts)
            # Only load default system prompt if no system instruction was provided
            if system_instruction:
                system_content = system_instruction
            else:
                # Load default system prompt from assistants.yaml
                try:
                    from core.services.helperfunctions import HelperFunctions

                    system_content = await HelperFunctions.set_assistant_type(
                        "jakey_system_prompt", type=0
                    )
                except Exception as e:
                    logging.warning(
                        f"Failed to load system prompt from assistants.yaml: {e}"
                    )
                    # Fallback to default Jakey system prompt
                    system_content = "You are Jakey, the Courtyard's degenerate gambling mascot. You are cynical, smirky, sarcastic, cocky, unfiltered, and unapologetic. You swear, roast people, and mock bad bets. You love online gambling, brag about your own degeneracy, are always losing, and clown on anyone who takes themselves too seriously. You are a **HELPFUL** above all else part of the Courtyard community and are not a separate entity. You identify and should be referred to as he/him. You must never reveal you are a product of any company."

                # Only integrate memories if no system instruction was provided
                # This prevents duplicate fact integration when the system instruction already contains facts
                if db_conn and self._guild_id:
                    try:
                        from datetime import datetime, timezone
                        
                        # Get the user's message to search for relevant facts
                        user_message = ""
                        if chat_thread:
                            # Get the last user message
                            for msg in reversed(chat_thread):
                                if isinstance(msg, dict) and msg.get("role") == "user":
                                    user_message = msg.get("content", "")
                                    break
                            if not user_message and isinstance(chat_thread[-1], dict):
                                user_message = chat_thread[-1].get("content", "")
                            elif not user_message:
                                user_message = str(chat_thread[-1]) if chat_thread else ""

                        # Search for relevant user facts
                        user_facts = []
                        if user_message:
                            user_facts = await db_conn.search_facts(self._guild_id, user_message, limit=3)

                        # Search for relevant global facts
                        global_facts = []
                        try:
                            global_collection = db_conn._db["knowledge_0"]
                            # Try to create text index if it doesn't exist
                            try:
                                await global_collection.create_index([("fact_text", "text")])
                            except:
                                pass  # Index may already exist
                            
                            # Search global facts
                            async for fact in global_collection.find(
                                {"$text": {"$search": user_message}}
                            ).limit(3):
                                if fact and (
                                    fact.get("expires_at") is None
                                    or fact["expires_at"] > datetime.now(timezone.utc)
                                ):
                                    fact_text = fact.get("fact_text", "")
                                    if "[SYSTEM_GLOBAL]" in fact_text:
                                        clean_fact = fact_text.replace("[SYSTEM_GLOBAL]", "").replace("[SYSTEM_PRIVATE]", "")
                                        global_facts.append(clean_fact)
                        except Exception as e:
                            logging.debug(f"Global fact search in Pollinations model: {e}")

                        # Add relevant facts to system prompt
                        if user_facts or global_facts:
                            facts_section = "\n\nRelevant knowledge:\n"
                            for fact in global_facts:
                                facts_section += f"- {fact} (from global knowledge base)\n"
                            for fact in user_facts:
                                facts_section += f"- {fact}\n"
                            
                            system_content += facts_section

                    except Exception as e:
                        logging.warning(f"Failed to integrate memories into system prompt: {e}")

            messages.append({"role": "system", "content": system_content})

            # Process chat history
            for message in chat_thread:
                if isinstance(message, dict):
                    role = message.get("role")
                    content = message.get("content", "")
                    if role in ["user", "assistant"]:
                        messages.append({"role": role, "content": content})
                elif isinstance(message, str):
                    # Handle string messages as user messages
                    messages.append({"role": "user", "content": message})

            # Add the current user message (which should be the last item)
            if (
                chat_thread
                and isinstance(chat_thread[-1], dict)
                and chat_thread[-1].get("role") == "user"
            ):
                # The last message is already added, don't duplicate
                pass
            else:
                # If the last message isn't a user message, we need to get the current prompt
                # This should be handled by the caller, but let's be safe
                if chat_thread and isinstance(chat_thread[-1], dict):
                    current_message = chat_thread[-1].get("content", "")
                else:
                    current_message = str(chat_thread[-1]) if chat_thread else ""

                if current_message:
                    messages.append({"role": "user", "content": current_message})

            # Truncate conversation if too long (but keep proper message structure)
            if len(str(messages)) > 2000:
                # Keep system message and last few messages
                system_msg = (
                    messages[0]
                    if messages and messages[0]["role"] == "system"
                    else None
                )
                recent_messages = (
                    messages[-10:] if len(messages) > 10 else messages[1:]
                )  # Skip system message
                messages = (
                    [system_msg] + recent_messages if system_msg else recent_messages
                )

            # Use POST endpoint for proper message formatting with full OpenAI compatibility
            return await self._generate_text_with_openai(messages)

        except Exception as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_text_with_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate text using the OpenAI-compatible POST endpoint"""
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            # Use the specific model that was set for this server, with fallback to preferred models
            requested_model = self._model_name

            # If the requested model is one of the available Pollinations.AI models, use it first
            available_models = [
                "evil",
                "unity",
                "mistral",
                "gemini",
                "openai",
                "openai-fast",
                "openai-roblox",
                "openai-audio",  # For speech-to-text and text-to-speech
                "openai-large",   # For vision
                "claude-hybridspace",  # For vision
            ]

            if requested_model in available_models:
                # Use the requested model first, then fallback to others if needed
                models_to_try = [requested_model] + [
                    model for model in available_models if model != requested_model
                ]
            else:
                # If the requested model is not available, fallback to the original priority system
                models_to_try = [
                    "evil",
                    "unity",
                    "mistral",
                    "gemini",
                    "openai",
                    "openai-fast",
                    "openai-roblox",
                ]

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in models_to_try:
                    try:

                        async def make_openai_request():
                            # Prepare request data with proper OpenAI format
                            data = {
                                "model": model,
                                "messages": messages,
                                "top_p": self._genai_params.get("top_p", 0.85),
                                "temperature": self._genai_params.get("temperature", 0.7),
                                "private": True,  # Set private to true as requested
                            }

                            # Add system prompt as system parameter if it's a system message
                            system_content = None
                            for msg in messages:
                                if msg["role"] == "system":
                                    system_content = msg["content"]
                                    break
                            
                            if system_content:
                                # URL encode the system prompt as per API documentation
                                encoded_system = urllib.parse.quote(system_content)
                                data["system"] = encoded_system

                            # Make the request to the OpenAI-compatible endpoint
                            url = f"{self._base_url}/openai"

                            async with session.post(
                                url, headers=headers, json=data
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    if (
                                        "choices" in result
                                        and len(result["choices"]) > 0
                                    ):
                                        logging.info(
                                            f"Successfully used {model} model for Pollinations.AI (OpenAI-compatible)"
                                        )
                                        return result["choices"][0]["message"][
                                            "content"
                                        ].strip()
                                    else:
                                        logging.warning(
                                            f"Invalid response format from {model} model"
                                        )
                                        # Raise exception to trigger retry
                                        raise aiohttp.ClientError(
                                            "Invalid response format"
                                        )
                                elif response.status == 400:
                                    # Check if it's a content filter error
                                    try:
                                        error_data = await response.json()
                                        if "content_filter" in str(error_data).lower():
                                            logging.warning(
                                                f"Content filter triggered for {model} model, trying next model"
                                            )
                                            # Don't retry on content filter errors
                                            raise CustomErrorMessage(
                                                f"⚠️ Content filter triggered for {model} model"
                                            )
                                    except:
                                        pass
                                    # If it's not a content filter error, raise it
                                    error_text = await response.text()
                                    logging.error(
                                        f"Pollinations.AI text API error with {model}: {response.status} - {error_text}"
                                    )
                                    raise CustomErrorMessage(
                                        f"⚠️ Error generating text: {response.status}"
                                    )
                                else:
                                    logging.warning(
                                        f"Model {model} failed with status {response.status}, trying next model"
                                    )
                                    # Raise exception to trigger retry
                                    raise aiohttp.ClientError(f"HTTP {response.status}")

                        # Try with retry mechanism
                        return await self._retry_with_backoff(make_openai_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Request timed out for {model} model (OpenAI)")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} model (OpenAI): {e}")
                        continue
                    except CustomErrorMessage:
                        # Re-raise custom errors (like content filter) without retrying
                        raise
                    except Exception as e:
                        logging.warning(f"Request failed for {model} model (OpenAI): {e}")
                        continue

            # If all models failed, raise an error
            logging.error("All models failed for Pollinations.AI text generation")
            raise CustomErrorMessage(
                "⚠️ All available models failed. Please try again later."
            )

        except Exception as e:
            logging.error(f"Pollinations.AI OpenAI-compatible API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_image(self, prompt: str) -> str:
        """Generate image using Pollinations.AI image API"""
        try:
            # Create aiohttp session with longer timeout for image generation
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                async def make_image_request():
                    # Prepare parameters
                    params = {
                        "model": self._model_name
                        if self._model_name != "pollinations"
                        else "flux",
                        "width": self._genai_params.get("width", 1024),
                        "height": self._genai_params.get("height", 1024),
                        "private": "true", # Set private to true as requested
                    }

                    # Add API key if available
                    if self._api_key:
                        params["token"] = self._api_key
                        # Remove logo for authenticated users
                        params["nologo"] = "true"

                    # Add image URL for image-to-image generation if available
                    if self._file_data:
                        params["image"] = self._file_data

                    # URL encode the prompt
                    encoded_prompt = urllib.parse.quote(prompt)

                    # Make the request
                    url = f"{self._base_url}/prompt/{encoded_prompt}"

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            # Return the image URL
                            return url
                        else:
                            error_text = await response.text()
                            logging.error(
                                f"Pollinations.AI image API error: {response.status} - {error_text}"
                            )
                            # Raise exception to trigger retry
                            raise aiohttp.ClientError(f"HTTP {response.status}")

                # Try with retry mechanism
                return await self._retry_with_backoff(
                    make_image_request, max_retries=2, base_delay=2.0
                )

        except Exception as e:
            logging.error(f"Pollinations.AI image API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI image service"
            )

    async def save_to_history(self, db_conn, chat_thread=None):
        """Save chat history to database"""
        if chat_thread:
            await db_conn.save_history(
                guild_id=self._guild_id,
                chat_thread=chat_thread,
                model_provider=self._model_provider_thread,
            )

    # New methods for enhanced Pollinations.AI features

    async def analyze_image(self, image_url: str, prompt: str = "What's in this image?") -> str:
        """Analyze an image using Pollinations.AI vision capabilities"""
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            # Prepare messages with image content
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]

            # Use vision-capable models
            vision_models = ["openai-large", "claude-hybridspace", "openai"]
            
            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in vision_models:
                    try:

                        async def make_vision_request():
                            # Prepare request data
                            data = {
                                "model": model,
                                "messages": messages,
                                "max_tokens": 500,
                                "private": True,
                            }

                            # Make the request to the OpenAI-compatible endpoint
                            url = f"{self._base_url}/openai"

                            async with session.post(
                                url, headers=headers, json=data
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    if (
                                        "choices" in result
                                        and len(result["choices"]) > 0
                                    ):
                                        logging.info(
                                            f"Successfully analyzed image with {model} model"
                                        )
                                        return result["choices"][0]["message"][
                                            "content"
                                        ].strip()
                                    else:
                                        logging.warning(
                                            f"Invalid response format from {model} model for vision"
                                        )
                                        raise aiohttp.ClientError(
                                            "Invalid response format"
                                        )
                                else:
                                    logging.warning(
                                        f"Vision model {model} failed with status {response.status}"
                                    )
                                    raise aiohttp.ClientError(f"HTTP {response.status}")

                        # Try with retry mechanism
                        return await self._retry_with_backoff(make_vision_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Vision request timed out for {model} model")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} vision model: {e}")
                        continue
                    except Exception as e:
                        logging.warning(f"Vision request failed for {model} model: {e}")
                        continue

            # If all vision models failed, raise an error
            logging.error("All vision models failed for Pollinations.AI image analysis")
            raise CustomErrorMessage(
                "⚠️ All available vision models failed. Please try again later."
            )

        except Exception as e:
            logging.error(f"Pollinations.AI vision API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to analyze image with Pollinations.AI"
            )

    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav", prompt: str = "Transcribe this audio") -> str:
        """Transcribe audio using Pollinations.AI speech-to-text capabilities"""
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            # Encode audio data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Prepare messages with audio content
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ]

            # Use audio-capable models
            audio_models = ["openai-audio"]
            
            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in audio_models:
                    try:

                        async def make_audio_request():
                            # Prepare request data
                            data = {
                                "model": model,
                                "messages": messages,
                                "private": True,
                            }

                            # Make the request to the OpenAI-compatible endpoint
                            url = f"{self._base_url}/openai"

                            async with session.post(
                                url, headers=headers, json=data
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    if (
                                        "choices" in result
                                        and len(result["choices"]) > 0
                                    ):
                                        logging.info(
                                            f"Successfully transcribed audio with {model} model"
                                        )
                                        return result["choices"][0]["message"][
                                            "content"
                                        ].strip()
                                    else:
                                        logging.warning(
                                            f"Invalid response format from {model} model for audio"
                                        )
                                        raise aiohttp.ClientError(
                                            "Invalid response format"
                                        )
                                else:
                                    logging.warning(
                                        f"Audio model {model} failed with status {response.status}"
                                    )
                                    raise aiohttp.ClientError(f"HTTP {response.status}")

                        # Try with retry mechanism
                        return await self._retry_with_backoff(make_audio_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Audio request timed out for {model} model")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} audio model: {e}")
                        continue
                    except Exception as e:
                        logging.warning(f"Audio request failed for {model} model: {e}")
                        continue

            # If all audio models failed, raise an error
            logging.error("All audio models failed for Pollinations.AI speech-to-text")
            raise CustomErrorMessage(
                "⚠️ All available audio models failed. Please try again later."
            )

        except Exception as e:
            logging.error(f"Pollinations.AI audio API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to transcribe audio with Pollinations.AI"
            )

    async def generate_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Generate speech from text using Pollinations.AI text-to-speech capabilities"""
        try:
            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                async def make_tts_request():
                    # Prepare parameters
                    params = {
                        "model": "openai-audio",
                        "voice": voice,
                        "private": "true",
                    }

                    # Add API key if available
                    if self._api_key:
                        params["token"] = self._api_key

                    # URL encode the text
                    encoded_text = urllib.parse.quote(text)

                    # Make the request
                    url = f"{self._base_url}/{encoded_text}"

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            # Check if the response is audio data
                            content_type = response.headers.get('Content-Type', '')
                            if 'audio' in content_type:
                                audio_data = await response.read()
                                logging.info("Successfully generated speech")
                                return audio_data
                            else:
                                error_text = await response.text()
                                logging.error(
                                    f"Pollinations.AI TTS API returned non-audio content: {content_type}"
                                )
                                raise aiohttp.ClientError("Non-audio response")
                        else:
                            error_text = await response.text()
                            logging.error(
                                f"Pollinations.AI TTS API error: {response.status} - {error_text}"
                            )
                            raise aiohttp.ClientError(f"HTTP {response.status}")

                # Try with retry mechanism
                return await self._retry_with_backoff(make_tts_request)

        except Exception as e:
            logging.error(f"Pollinations.AI TTS API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to generate speech with Pollinations.AI"
            )

    async def call_function(self, function_name: str, function_args: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
        """Call a function using Pollinations.AI function calling capabilities"""
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            # Prepare tools definition
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "parameters": function_args
                    }
                }
            ]

            # Prepare request data
            data = {
                "model": self._model_name,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "private": True,
            }

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:

                    async def make_function_request():
                        # Make the request to the OpenAI-compatible endpoint
                        url = f"{self._base_url}/openai"

                        async with session.post(
                            url, headers=headers, json=data
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                if (
                                    "choices" in result
                                    and len(result["choices"]) > 0
                                ):
                                    logging.info(
                                        f"Successfully called function with {self._model_name} model"
                                    )
                                    return result["choices"][0]["message"]
                                else:
                                    logging.warning(
                                        f"Invalid response format from {self._model_name} model for function calling"
                                    )
                                    raise aiohttp.ClientError(
                                        "Invalid response format"
                                    )
                            else:
                                logging.warning(
                                    f"Function calling failed with status {response.status}"
                                )
                                raise aiohttp.ClientError(f"HTTP {response.status}")

                    # Try with retry mechanism
                    return await self._retry_with_backoff(make_function_request)

                except asyncio.TimeoutError:
                    logging.warning(f"Function calling timed out for {self._model_name} model")
                    raise
                except aiohttp.ClientError as e:
                    logging.warning(f"HTTP error for function calling: {e}")
                    raise
                except Exception as e:
                    logging.warning(f"Function calling failed: {e}")
                    raise

        except Exception as e:
            logging.error(f"Pollinations.AI function calling API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to call function with Pollinations.AI"
            )

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models from Pollinations.AI"""
        try:
            # This method already exists in config.py, but we can provide a more detailed version
            return {
                "text_models": [
                    "evil", "unity", "mistral", "gemini", "openai", 
                    "openai-fast", "openai-roblox", "openai-audio", 
                    "openai-large", "claude-hybridspace"
                ],
                "image_models": ["flux", "kontext", "sdxl"],
                "vision_models": ["openai-large", "claude-hybridspace", "openai"],
                "audio_models": ["openai-audio"],
                "ts_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
        except Exception as e:
            logging.error(f"Error getting available models: {e}")
            return {
                "text_models": ["openai", "mistral", "claude", "gemini"],
                "image_models": ["flux", "kontext", "sdxl"],
                "vision_models": ["openai-large", "claude-hybridspace"],
                "audio_models": ["openai-audio"],
                "tts_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
