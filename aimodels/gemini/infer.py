import logging

from .config import ModelParams
from core.ai.core import Utils
from core.exceptions import CustomErrorMessage
from core.services.colored_logging import log_error, log_warning
from google import genai
from google.genai import errors
from google.genai import types
from os import environ
from pathlib import Path
import aiohttp
import aiofiles
import asyncio
import discord
import io
import logging
import typing
import random


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

        # Check if _gemini_api_client is in the self._discord_bot object
        if not hasattr(discord_bot, "_gemini_api_client"):
            raise Exception(
                "Gemini API client for completions not initialized, please check the bot configuration"
            )

        # Check if _aiohttp_main_client_session is in the self._discord_bot object
        if not hasattr(discord_bot, "_aiohttp_main_client_session"):
            raise Exception(
                "aiohttp client session for get requests not initialized, please check the bot configuration"
            )

        self._gemini_api_client: genai.Client = discord_bot._gemini_api_client
        self._aiohttp_main_client_session: aiohttp.ClientSession = (
            discord_bot._aiohttp_main_client_session
        )

        self._model_name = model_name
        self._guild_id = guild_id

    async def input_files(self, attachment: discord.Attachment):
        # Download the attachment
        _xfilename = f"{environ.get('TEMP_DIR')}/JAKEY.{random.randint(518301839, 6582482111)}.{attachment.filename}"

        # Sometimes mimetype has text/plain; charset=utf-8, we need to grab the first part
        _mimetype = attachment.content_type.split(";")[0]
        try:
            async with self._aiohttp_main_client_session.get(
                attachment.url, allow_redirects=True
            ) as _xattachments:
                # write to file with random number ID
                async with aiofiles.open(_xfilename, "wb") as filepath:
                    async for _chunk in _xattachments.content.iter_chunked(8192):
                        await filepath.write(_chunk)
        except aiohttp.ClientError as httperror:
            # Remove the file if it exists ensuring no data persists even on failure
            if Path(_xfilename).exists():
                await aiofiles.os.remove(_xfilename)
            # Raise exception
            raise httperror

        # Upload the file
        _msgstatus = None
        try:
            _filedata = await self._gemini_api_client.aio.files.upload(
                file=_xfilename, config=types.UploadFileConfig(mime_type=_mimetype)
            )

            while _filedata.state == "PROCESSING":
                if _msgstatus is None:
                    _msgstatus = await self._discord_method_send(
                        f"⌚ Processing the file attachment, this may take longer than usual..."
                    )

                _filedata = await self._gemini_api_client.aio.files.get(
                    name=_filedata.name
                )
                await asyncio.sleep(2.5)
        except Exception as e:
            raise e
        finally:
            if _msgstatus:
                await _msgstatus.delete()
            await aiofiles.os.remove(_xfilename)

        self._file_data = [
            types.Part.from_uri(
                file_uri=_filedata.uri, mime_type=_filedata.mime_type
            ).model_dump(exclude_unset=True)
        ]

    ############################
    # Inferencing
    ############################
    # Completion
    async def completion(
        self,
        prompt: typing.Union[str, list, types.Content],
        tool: dict = None,
        system_instruction: str = None,
        return_text: bool = True,
    ):
        # Normalize model names to "-nonthinking"
        if self._model_name.endswith("-nonthinking"):
            self._model_name = self._model_name.replace("-nonthinking", "")

            logging.info(
                "Using non-thinking variant of the model: %s", self._model_name
            )

        # Create response
        _response = await self._gemini_api_client.aio.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                **self._genai_params,
                system_instruction=system_instruction,
                tools=tool,  # Pass the tool schema in config to enable function calling
            ),
        )

        if return_text:
            return _response.text
        else:
            return _response

    async def _auto_enable_tool_if_needed(self, function_name: str, db_conn) -> bool:
        """
        Automatically enable a tool if Jakey tries to use it but it's not currently enabled.

        Args:
            function_name: The function name that Jakey is trying to call
            db_conn: Database connection for updating tool configuration

        Returns:
            bool: True if tool was enabled, False if not needed or failed
        """
        # Map function names to tool names
        function_to_tool_map = {
            "web_search": "ExaSearch",
            "get_token_price": "CryptoPrice",
            "convert_currency": "CurrencyConverter",
            "github_file_tool": "GitHub",
            "github_search_tool": "GitHub",
            "youtube_search": "YouTube",
            "youtube_summarize": "YouTube",
            "create_audio": "AudioTools",
            "clone_voice": "AudioTools",
            "generate_canvas": "IdeationTools",
            "create_artifact": "IdeationTools",
            "remember": "Memory",
            "recall": "Memory",
        }

        # Check if this function corresponds to a specific tool
        tool_name = function_to_tool_map.get(function_name)
        if not tool_name:
            return False

        try:
            # Get current tool configuration
            current_tool = await db_conn.get_tool_config(guild_id=self._guild_id)

            # If the tool is already enabled, no need to change
            if current_tool == tool_name:
                return False

            # Automatically enable the required tool
            await db_conn.set_tool_config(guild_id=self._guild_id, tool=tool_name)

            # Use auto return manager to set up timeout
            if hasattr(self._discord_bot, "auto_return_manager"):
                await self._discord_bot.auto_return_manager.switch_tool_with_timeout(
                    guild_id=self._guild_id,
                    new_tool=tool_name,
                    user_id=getattr(self._discord_ctx, "author", None),
                )

            # Log the automatic tool switch
            logging.info(
                f"Automatically enabled {tool_name} for guild {self._guild_id} when Jakey tried to use {function_name}"
            )

            # Send a brief notification to the user
            await self._discord_method_send(
                f"🔄 **Auto-enabled {tool_name}** - Jakey needed this tool to help you!"
            )

            return True

        except Exception as e:
            logging.error(f"Failed to auto-enable tool {tool_name}: {e}")
            return False

    async def chat_completion(self, prompt, db_conn, system_instruction: str = None):
        # Load history
        _chat_thread = await db_conn.load_history(
            guild_id=self._guild_id, model_provider=self._model_provider_thread
        )

        # Fetch tool
        _Tool = await self._fetch_tool(db_conn)

        if _chat_thread is None:
            _chat_thread = []

        # Craft prompt
        _prompt = {
            "role": "user",
            "parts": [types.Part.from_text(text=prompt).model_dump(exclude_unset=True)],
        }

        # Attach file attachment if it exists
        if hasattr(self, "_file_data"):
            _prompt["parts"].extend(self._file_data)

        _chat_thread.append(_prompt)

        # First response which is called only once
        try:
            _response = await self.completion(
                prompt=[_prompt],
                tool=_Tool["tool_schema"],
                system_instruction=system_instruction,
                return_text=False,
            )
        # Check if we get ClientError and has PERMISSION_DENIED
        except errors.ClientError as e:
            log_error(f"Gemini API client error (1st try): {e.message}")
            if "do not have permission" in e.message:
                # Curated history attribute are list of multipart chat turns under Content structured datatype
                # Inside, it has "part" -> List and "role" -> str fields, so we iterate on the parts
                for _chat_turns in _chat_thread:
                    for _part in _chat_turns["parts"]:
                        # Check if we have file_data key then we just set it as None and set the text to "Expired"
                        if _part.get("file_data"):
                            _part["file_data"] = None
                            _part["text"] = (
                                "[<system_notice>File attachment processed but expired from history. DO NOT make stuff up about it! Ask the user to reattach for more details</system_notice>]"
                            )

                # Notify the user that the chat session has been re-initialized
                await self._discord_method_send(
                    "> ⚠️ One or more file attachments or tools have been expired, the chat history has been reinitialized!"
                )

                # Retry the request
                _response = await self.completion(
                    prompt=_chat_thread,
                    tool=_Tool["tool_schema"],
                    system_instruction=system_instruction,
                    return_text=False,
                )
            elif e.status_code == 429:
                log_warning(
                    "Gemini API quota exceeded (429 RESOURCE_EXHAUSTED). Retrying after 30 seconds."
                )
                await self._discord_method_send(
                    "> ⚠️ Gemini API quota exceeded. Retrying your request in 30 seconds..."
                )
                await asyncio.sleep(30)  # Wait for 30 seconds as suggested by the error
                _response = await self.completion(
                    prompt=_chat_thread,
                    tool=_Tool["tool_schema"],
                    system_instruction=system_instruction,
                    return_text=False,
                )
            else:
                log_error(f"Gemini API client error (2nd try): {e.message}")
                raise e
        # Check if the response was blocked due to safety and other reasons than STOP
        # https://ai.google.dev/api/generate-content#FinishReason
        if hasattr(_response, "candidates") and _response.candidates:
            if _response.candidates[0].finish_reason == "SAFETY":
                raise CustomErrorMessage(
                    "🤬 I detected unsafe content in your prompt, Please rephrase your question."
                )
            elif _response.candidates[0].finish_reason == "MAX_TOKENS":
                raise CustomErrorMessage(
                    "⚠️ Response reached max tokens limit, please make your message concise."
                )
            elif _response.candidates[0].finish_reason != "STOP":
                log_error(
                    f"Gemini API error: finish_reason = {_response.candidates[0].finish_reason}"
                )
                raise CustomErrorMessage(
                    "⚠️ An error has occurred while giving you an answer, please rephrase your prompt or try again later."
                )
        else:
            # Handle cases where candidates is None or empty
            error_message = "⚠️ An error has occurred while giving you an answer, please rephrase your prompt or try again later."

            # Check for specific error conditions
            if hasattr(_response, "prompt_feedback") and _response.prompt_feedback:
                if hasattr(_response.prompt_feedback, "block_reason"):
                    block_reason = _response.prompt_feedback.block_reason
                    if block_reason == "PROHIBITED_CONTENT":
                        error_message = "🚫 Your message contains prohibited content. Please rephrase your question to be more appropriate."
                    elif block_reason == "SAFETY":
                        error_message = "🛡️ Your message was blocked for safety reasons. Please rephrase your question."
                    elif block_reason == "OTHER":
                        error_message = "⚠️ Your message was blocked. Please try rephrasing your question."
                    else:
                        error_message = f"🚫 Your message was blocked: {block_reason}. Please rephrase your question."

            log_error(f"Gemini API error: response blocked - {_response}")
            raise CustomErrorMessage(error_message)

        # Agentic experiences
        # Begin inference operation
        # Removed interstitial message variable
        _toolUseErrorOccurred = False
        while True:
            # Check for function calls
            _toolParts = []
            # Removed interstitial message for cleaner tool usage

            # Check for tools or other content to be sent
            for _part in _response.candidates[0].content.parts:
                # Send text message if needed
                if _part.text and _part.text.strip():
                    await Utils.send_ai_response(
                        self._discord_ctx, prompt, _part.text, self._discord_method_send
                    )

                if _part.function_call:
                    # Append the chat history here
                    _chat_thread.append(
                        _response.candidates[0].content.model_dump(exclude_unset=True)
                    )

                    try:
                        # Try to auto-enable the tool if needed
                        tool_was_enabled = await self._auto_enable_tool_if_needed(
                            _part.function_call.name, db_conn
                        )

                        # If we auto-enabled a tool, we need to reload the tool configuration
                        if tool_was_enabled:
                            _Tool = await self._fetch_tool(db_conn)

                        # Removed interstitial message edit for cleaner tool usage

                        if hasattr(
                            _Tool["tool_object"],
                            f"_tool_function_{_part.function_call.name}",
                        ):
                            _toExec = getattr(
                                _Tool["tool_object"],
                                f"_tool_function_{_part.function_call.name}",
                            )
                        elif hasattr(_Tool["tool_object"], "_tool_function"):
                            _toExec = getattr(_Tool["tool_object"], "_tool_function")
                        else:
                            log_error(
                                f"Tool function not found: {_part.function_call.name}"
                            )
                            raise CustomErrorMessage(
                                "⚠️ An error has occurred while calling tools, please try again later or choose another tool"
                            )

                        _toolResult = {
                            "toolResult": (await _toExec(**_part.function_call.args)),
                            "tool_args": _part.function_call.args,
                        }
                        _toolUseErrorOccurred = False
                    # For other exceptions, log the error and add it as part of the chat thread
                    except Exception as e:
                        # Must not set status to true if it was already set to False
                        if not _toolUseErrorOccurred:
                            _toolUseErrorOccurred = True

                        # Also print the error to the console
                        log_error(f"Tool execution error: {e}")
                        _toolResult = {
                            "error": f"⚠️ Something went wrong while executing the tool: {e}\nTell the user about this error and make sure the tool is enabled with the /feature command",
                            "tool_args": _part.function_call.args,
                        }

                    # Append the tool part to the chat thread
                    _toolParts.append(
                        types.Part.from_function_response(
                            name=_part.function_call.name, response=_toolResult
                        )
                    )

                # Function calling and code execution doesn't mix
                if _part.executable_code:
                    await self._discord_method_send(f"✅ Code analysis complete")
                    await self._discord_method_send(
                        f"```py\n{_part.executable_code.code[:1975]}\n```"
                    )

                if _part.code_execution_result:
                    if _part.code_execution_result.output:
                        # Send the code execution result
                        await self._discord_method_send(
                            f"```{_part.code_execution_result.output[:1975]}```"
                        )

                # Render the code execution inline data when needed
                if _part.inline_data:
                    if _part.inline_data.mime_type == "image/png":
                        await self._discord_method_send(
                            file=discord.File(
                                io.BytesIO(_part.inline_data.data), filename="image.png"
                            )
                        )
                    elif _part.inline_data.mime_type == "image/jpeg":
                        await self._discord_method_send(
                            file=discord.File(
                                io.BytesIO(_part.inline_data.data),
                                filename="image.jpeg",
                            )
                        )
                    else:
                        await self._discord_method_send(
                            file=discord.File(
                                io.BytesIO(_part.inline_data.data),
                                filename="code_exec_artifact.bin",
                            )
                        )

            # Handle tool execution results
            if _toolParts:
                # Removed interstitial message handling for cleaner tool usage

                # Append the tool parts to the chat thread
                _chat_thread.append(
                    types.Content(parts=_toolParts, role="user").model_dump(
                        exclude_unset=True
                    )
                )

                # Add function call parts to the response
                _response = await self.completion(
                    prompt=_chat_thread,
                    tool=_Tool["tool_schema"],
                    system_instruction=system_instruction,
                    return_text=False,
                )

                _filtered_parts = []
                for part in _response.candidates[0].content.parts:
                    if part.text:
                        _filtered_parts.append(types.Part.from_text(text=part.text))
                        # Send the AI's response that integrates tool results to Discord
                        await self._discord_method_send(part.text)
                    elif part.function_call:
                        try:
                            # Try the newer version signature first
                            _filtered_parts.append(
                                types.Part.from_function_call(part.function_call)
                            )
                        except TypeError:
                            # Fallback to older version signature if needed
                            _filtered_parts.append(
                                types.Part.from_function_call(
                                    function_call=part.function_call
                                )
                            )

                _chat_thread.append(
                    types.Content(
                        parts=_filtered_parts, role=_response.candidates[0].content.role
                    ).model_dump(exclude_unset=True)
                )

            # Assuming we are done with the response and continue statement isn't triggered
            break

        # Done
        # Append the chat thread and send the status response
        _filtered_parts = []
        for part in _response.candidates[0].content.parts:
            if part.text:
                _filtered_parts.append(types.Part.from_text(text=part.text))
            elif part.function_call:
                try:
                    # Try the newer version signature first
                    _filtered_parts.append(
                        types.Part.from_function_call(part.function_call)
                    )
                except TypeError:
                    # Fallback to older version signature if needed
                    _filtered_parts.append(
                        types.Part.from_function_call(function_call=part.function_call)
                    )

        _chat_thread.append(
            types.Content(
                parts=_filtered_parts, role=_response.candidates[0].content.role
            ).model_dump(exclude_unset=True)
        )
        return {"response": "OK", "chat_thread": _chat_thread}

    async def save_to_history(self, db_conn, chat_thread=None):
        await db_conn.save_history(
            guild_id=self._guild_id,
            chat_thread=chat_thread,
            model_provider=self._model_provider_thread,
        )
