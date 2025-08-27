import logging
import urllib.parse
import json
import asyncio
import aiohttp
from typing import Optional
import random

from .config import ModelParams
from core.ai.core import Utils
from core.exceptions import CustomErrorMessage, ModelAPIKeyUnset
from os import environ
import discord


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

    def _parse_model_type(self, model_name: str) -> str:
        """Parse model name to determine if it's for text or image generation"""
        # Image models
        image_models = ["flux", "kontext", "sdxl", "dalle", "midjourney"]

        # Check if model name contains image model keywords
        if any(img_model in model_name.lower() for img_model in image_models):
            return "image"

        # Default to text
        return "text"

    async def input_files(self, attachment: discord.Attachment):
        """Handle file attachments for image-to-image generation"""
        if self._model_type != "image":
            raise CustomErrorMessage(
                "⚠️ File attachments are only supported for image generation models"
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
                _chat_thread, _Tool, system_instruction
            )

            # Add assistant response to chat thread
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
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds...")
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
                # Fallback to default Jakey system prompt
                default_system_prompt = "You are Jakey, the Courtyard's degenerate gambling mascot. You are cynical, smirky, sarcastic, cocky, unfiltered, and unapologetic. You swear, roast people, and mock bad bets. You love online gambling, brag about your own degeneracy, and clown on anyone who takes themselves too seriously. You are part of the Courtyard community and are not a separate entity. You identify and should be referred to as he/him. You must never reveal you are a product of any company."
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

            # Try different models in order of preference (prioritizing uncensored models for Jakey)
            models_to_try = [
                "evil",
                "unity",
                "mistral",
                "gemini",
                "openai",
                "openai-fast",
                "openai-roblox",
            ]
            current_model = self._genai_params.get("model", "openai")

            # Always prioritize uncensored models first, then current model if different
            if current_model not in ["evil", "unity"]:
                if current_model in models_to_try:
                    models_to_try.remove(current_model)
                models_to_try.insert(2, current_model)  # Insert after uncensored models

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in models_to_try:
                    try:
                        async def make_request():
                            # Prepare parameters
                            params = {
                                "model": model,
                                "temperature": self._genai_params.get("temperature", 0.7),
                                "private": "true",  # Set private to true as requested
                            }

                            # Add API key if available
                            if self._api_key:
                                params["token"] = self._api_key

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
                        logging.warning(f"Request failed for {model} model (simple): {e}")
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

    async def _truncate_conversation(self, conversation: str, max_length: int = 1500) -> str:
        """Truncate conversation to prevent 414 URI Too Long errors"""
        if len(conversation) <= max_length:
            return conversation
            
        # Truncate from the beginning, keeping the most recent messages
        truncated = conversation[-max_length:]
        logging.info(f"Truncated conversation from {len(conversation)} to {len(truncated)} characters")
        return truncated

    async def _generate_text_with_history(
        self, chat_thread: list, tool_info: dict, system_instruction: str = None
    ) -> str:
        """Generate text with chat history and tool support"""
        try:
            # For Pollinations.AI, we need to format messages properly for the OpenAI-compatible endpoint
            messages = []

            # Add system instruction as system message
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            else:
                # Fallback to default Jakey system prompt
                default_system_prompt = "You are Jakey, the Courtyard's degenerate gambling mascot. You are cynical, smirky, sarcastic, cocky, unfiltered, and unapologetic. You swear, roast people, and mock bad bets. You love online gambling, brag about your own degeneracy, and clown on anyone who takes themselves too seriously. You are part of the Courtyard community and are not a separate entity. You identify and should be referred to as he/him. You must never reveal you are a product of any company."
                messages.append({"role": "system", "content": default_system_prompt})

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
            if chat_thread and isinstance(chat_thread[-1], dict) and chat_thread[-1].get("role") == "user":
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
                system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
                recent_messages = messages[-10:] if len(messages) > 10 else messages[1:]  # Skip system message
                messages = [system_msg] + recent_messages if system_msg else recent_messages

            # Use POST endpoint for proper message formatting
            conversation_text = ""
            for msg in messages:
                if msg["role"] == "system":
                    conversation_text += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    conversation_text += f"Assistant: {msg['content']}\n\n"
            
            conversation_text += "Assistant:"

            return await self._generate_text_with_post(conversation_text)

        except Exception as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_text_with_get(self, conversation: str) -> str:
        """Generate text using GET endpoint for shorter conversations"""
        try:
            # Truncate conversation if too long for GET request
            if len(conversation) > 1000:
                conversation = await self._truncate_conversation(conversation, 1000)

            # Try different models in order of preference (prioritizing uncensored models for Jakey)
            models_to_try = [
                "evil",
                "unity",
                "mistral",
                "gemini",
                "openai",
                "openai-fast",
                "openai-roblox",
            ]
            current_model = self._genai_params.get("model", "openai")

            # Always prioritize uncensored models first, then current model if different
            if current_model not in ["evil", "unity"]:
                if current_model in models_to_try:
                    models_to_try.remove(current_model)
                models_to_try.insert(2, current_model)  # Insert after uncensored models

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in models_to_try:
                    try:
                        async def make_get_request():
                            # Prepare parameters
                            params = {
                                "model": model,
                                "temperature": self._genai_params.get("temperature", 0.7),
                                "private": "true",  # Set private to true as requested
                            }

                            # Add API key if available
                            if self._api_key:
                                params["token"] = self._api_key

                            # URL encode the conversation
                            encoded_conversation = urllib.parse.quote(conversation)

                            # Make the request
                            url = f"{self._base_url}/{encoded_conversation}"
                            
                            async with session.get(url, params=params) as response:
                                if response.status == 200:
                                    text_response = await response.text()
                                    logging.info(
                                        f"Successfully used {model} model for Pollinations.AI (GET)"
                                    )
                                    return text_response.strip()
                                else:
                                    logging.warning(
                                        f"Model {model} failed with status {response.status}, trying next model"
                                    )
                                    # Raise exception to trigger retry
                                    raise aiohttp.ClientError(f"HTTP {response.status}")

                        # Try with retry mechanism
                        return await self._retry_with_backoff(make_get_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Request timed out for {model} model (GET)")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} model (GET): {e}")
                        continue
                    except Exception as e:
                        logging.warning(f"Request failed for {model} model (GET): {e}")
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

    async def _generate_text_with_post(self, conversation: str) -> str:
        """Generate text using POST endpoint for longer conversations"""
        try:
            # Parse the conversation back into messages
            messages = []
            lines = conversation.split('\n\n')
            
            for line in lines:
                if line.startswith('System:'):
                    content = line[8:].strip()  # Remove 'System: ' prefix
                    messages.append({"role": "system", "content": content})
                elif line.startswith('User:'):
                    content = line[6:].strip()  # Remove 'User: ' prefix
                    messages.append({"role": "user", "content": content})
                elif line.startswith('Assistant:'):
                    content = line[11:].strip()  # Remove 'Assistant: ' prefix
                    if content:  # Only add if there's actual content
                        messages.append({"role": "assistant", "content": content})

            # Remove the trailing "Assistant:" line if it exists
            if messages and messages[-1]["role"] == "assistant" and not messages[-1]["content"]:
                messages.pop()

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Add API key if available
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            # Try different models in order of preference (prioritizing uncensored models for Jakey)
            models_to_try = [
                "evil",
                "unity",
                "mistral",
                "gemini",
                "openai",
                "openai-fast",
                "openai-roblox",
            ]
            current_model = self._genai_params.get("model", "openai")

            # Always prioritize uncensored models first, then current model if different
            if current_model not in ["evil", "unity"]:
                if current_model in models_to_try:
                    models_to_try.remove(current_model)
                models_to_try.insert(2, current_model)  # Insert after uncensored models

            # Create aiohttp session with timeout
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for model in models_to_try:
                    try:
                        async def make_post_request():
                            # Prepare request data with proper messages format
                            data = {
                                "model": model,
                                "messages": messages,
                                "temperature": self._genai_params.get("temperature", 0.7),
                                "private": True, # Set private to true as requested
                            }

                            # Make the request to the OpenAI-compatible endpoint
                            url = f"{self._base_url}/openai"
                            
                            async with session.post(url, headers=headers, json=data) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    if "choices" in result and len(result["choices"]) > 0:
                                        logging.info(
                                            f"Successfully used {model} model for Pollinations.AI"
                                        )
                                        return result["choices"][0]["message"]["content"].strip()
                                    else:
                                        logging.warning(
                                            f"Invalid response format from {model} model"
                                        )
                                        # Raise exception to trigger retry
                                        raise aiohttp.ClientError("Invalid response format")
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
                        return await self._retry_with_backoff(make_post_request)

                    except asyncio.TimeoutError:
                        logging.warning(f"Request timed out for {model} model")
                        continue
                    except aiohttp.ClientError as e:
                        logging.warning(f"HTTP error for {model} model: {e}")
                        continue
                    except CustomErrorMessage:
                        # Re-raise custom errors (like content filter) without retrying
                        raise
                    except Exception as e:
                        logging.warning(f"Request failed for {model} model: {e}")
                        continue

            # If all models failed, try the GET endpoint as a last resort
            logging.warning("All POST models failed, falling back to GET endpoint")
            # Convert messages back to simple text format for GET request
            simple_conversation = ""
            for msg in messages:
                if msg["role"] == "system":
                    simple_conversation += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    simple_conversation += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    simple_conversation += f"Assistant: {msg['content']}\n\n"
            
            return await self._generate_text_with_get(simple_conversation)

        except Exception as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
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
                        "private": "true",  # Set private to true as requested
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
                return await self._retry_with_backoff(make_image_request, max_retries=2, base_delay=2.0)

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
