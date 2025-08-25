import logging
import requests
import urllib.parse
import json
import asyncio
from typing import Optional

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

    async def _generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """Generate text using Pollinations.AI text API"""
        try:
            # Add system instruction if provided
            if system_instruction:
                # For Pollinations.AI, we'll prepend the system instruction to the prompt
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

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

            for model in models_to_try:
                try:
                    # Prepare parameters
                    params = {
                        "model": model,
                        "temperature": self._genai_params.get("temperature", 0.7),
                        "private": "true",  # Set private to true as requested
                    }

                    # Add API key if available
                    if self._api_key:
                        params["token"] = self._api_key

                    # URL encode the prompt
                    encoded_prompt = urllib.parse.quote(full_prompt)

                    # Make the request
                    url = f"{self._base_url}/{encoded_prompt}"
                    response = requests.get(url, params=params, timeout=60)

                    if response.status_code == 200:
                        logging.info(
                            f"Successfully used {model} model for Pollinations.AI (simple)"
                        )
                        return response.text.strip()
                    else:
                        logging.warning(
                            f"Model {model} failed with status {response.status_code}, trying next model"
                        )
                        continue

                except requests.exceptions.RequestException as e:
                    logging.warning(f"Request failed for {model} model (simple): {e}")
                    continue

            # If all models failed, raise an error
            logging.error("All models failed for Pollinations.AI text generation")
            raise CustomErrorMessage(
                "⚠️ All available models failed. Please try again later."
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_text_with_history(
        self, chat_thread: list, tool_info: dict, system_instruction: str = None
    ) -> str:
        """Generate text with chat history and tool support"""
        try:
            # For Pollinations.AI, we'll format the chat history as a simple conversation
            conversation = ""

            # Add some debugging
            logging.debug(f"Processing chat thread with {len(chat_thread)} items")

            # Check if we have a system message in the chat thread
            has_system_message = False
            for message in chat_thread:
                if isinstance(message, dict) and message.get("role") == "system":
                    has_system_message = True
                    break

            # If no system message found, add the system instruction
            if not has_system_message and system_instruction:
                conversation += f"System: {system_instruction}\n\n"
            elif not has_system_message:
                # Fallback to default Jakey system prompt
                conversation += "System: You are Jakey, the Courtyard's degenerate gambling mascot. You are cynical, smirky, sarcastic, cocky, unfiltered, and unapologetic. You swear, roast people, and mock bad bets. You love online gambling, brag about your own degeneracy, and clown on anyone who takes themselves too seriously. You are part of the Courtyard community and are not a separate entity. You identify and should be referred to as he/him. You must never reveal you are a product of any company.\n\n"

            # Handle chat history structure - first item might be a time context string
            for i, message in enumerate(chat_thread):
                if i == 0 and isinstance(message, str):
                    # This is the time context string, skip it for now
                    logging.debug(f"Skipping time context string: {message[:50]}...")
                    continue

                # Handle message dictionaries
                if isinstance(message, dict):
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    if role == "system":
                        conversation += f"System: {content}\n\n"
                    elif role == "user":
                        conversation += f"User: {content}\n\n"
                    elif role == "assistant":
                        conversation += f"Assistant: {content}\n\n"
                    else:
                        logging.warning(f"Unknown role '{role}' in message: {message}")
                # Handle string messages (fallback)
                elif isinstance(message, str):
                    conversation += f"User: {message}\n\n"
                else:
                    logging.warning(f"Unknown message type {type(message)}: {message}")

            # Add the current user message (which should be the last item)
            if chat_thread and isinstance(chat_thread[-1], dict):
                current_message = chat_thread[-1].get("content", "")
            else:
                current_message = str(chat_thread[-1]) if chat_thread else ""

            conversation += f"User: {current_message}\n\nAssistant:"

            # Check if the conversation is too long for GET request
            if len(conversation) > 2000:  # Conservative limit to avoid 431 errors
                # Use POST endpoint for longer conversations
                return await self._generate_text_with_post(conversation)
            else:
                # Use GET endpoint for shorter conversations
                return await self._generate_text_with_get(conversation)

        except requests.exceptions.RequestException as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_text_with_get(self, conversation: str) -> str:
        """Generate text using GET endpoint for shorter conversations"""
        try:
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

            for model in models_to_try:
                try:
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
                    response = requests.get(url, params=params, timeout=60)

                    if response.status_code == 200:
                        logging.info(
                            f"Successfully used {model} model for Pollinations.AI (GET)"
                        )
                        return response.text.strip()
                    else:
                        logging.warning(
                            f"Model {model} failed with status {response.status_code}, trying next model"
                        )
                        continue

                except requests.exceptions.RequestException as e:
                    logging.warning(f"Request failed for {model} model (GET): {e}")
                    continue

            # If all models failed, raise an error
            logging.error("All models failed for Pollinations.AI text generation")
            raise CustomErrorMessage(
                "⚠️ All available models failed. Please try again later."
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_text_with_post(self, conversation: str) -> str:
        """Generate text using POST endpoint for longer conversations"""
        try:
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

            for model in models_to_try:
                try:
                    # Prepare request data
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": conversation}],
                        "temperature": self._genai_params.get("temperature", 0.7),
                        "private": True,  # Set private to true as requested
                    }

                    # Make the request to the OpenAI-compatible endpoint
                    url = f"{self._base_url}/openai"
                    response = requests.post(
                        url, headers=headers, json=data, timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            logging.info(
                                f"Successfully used {model} model for Pollinations.AI"
                            )
                            return result["choices"][0]["message"]["content"].strip()
                        else:
                            logging.warning(
                                f"Invalid response format from {model} model"
                            )
                            continue
                    elif response.status_code == 400:
                        # Check if it's a content filter error
                        try:
                            error_data = response.json()
                            if "content_filter" in str(error_data).lower():
                                logging.warning(
                                    f"Content filter triggered for {model} model, trying next model"
                                )
                                continue
                        except:
                            pass
                        # If it's not a content filter error, raise it
                        logging.error(
                            f"Pollinations.AI text API error with {model}: {response.status_code} - {response.text}"
                        )
                        raise CustomErrorMessage(
                            f"⚠️ Error generating text: {response.status_code}"
                        )
                    else:
                        logging.warning(
                            f"Model {model} failed with status {response.status_code}, trying next model"
                        )
                        continue

                except requests.exceptions.RequestException as e:
                    logging.warning(f"Request failed for {model} model: {e}")
                    continue

            # If all models failed, try the GET endpoint as a last resort
            logging.warning("All POST models failed, falling back to GET endpoint")
            return await self._generate_text_with_get(conversation)

        except requests.exceptions.RequestException as e:
            logging.error(f"Pollinations.AI text API request failed: {e}")
            raise CustomErrorMessage(
                "⚠️ Failed to connect to Pollinations.AI text service"
            )

    async def _generate_image(self, prompt: str) -> str:
        """Generate image using Pollinations.AI image API"""
        try:
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
            response = requests.get(
                url, params=params, timeout=120
            )  # Longer timeout for image generation

            if response.status_code == 200:
                # Return the image URL
                return url
            else:
                logging.error(
                    f"Pollinations.AI image API error: {response.status_code} - {response.text}"
                )
                raise CustomErrorMessage(
                    f"⚠️ Error generating image: {response.status_code}"
                )

        except requests.exceptions.RequestException as e:
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
