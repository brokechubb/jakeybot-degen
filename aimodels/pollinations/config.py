from core.exceptions import CustomErrorMessage
import importlib
import logging
import requests
import urllib.parse


class ModelParams:
    def __init__(self):
        # Model provider thread
        self._model_provider_thread = "pollinations"

        # Default parameters for Pollinations.AI
        self._genai_params = {
            "temperature": 0.7,
            "model": "openai",  # Default text model - will be overridden by actual model name
            "width": 1024,  # Default image width
            "height": 1024,  # Default image height
        }

    # internal function to fetch tool
    async def _fetch_tool(self, db_conn) -> dict:
        # Tools
        _tool_selection_name = await db_conn.get_tool_config(guild_id=self._guild_id)

        # Always include Memory tool as base tool
        _memory_tool = None
        try:
            _memory_tool = importlib.import_module("tools.Memory").Tool(
                method_send=self._discord_method_send,
                discord_ctx=self._discord_ctx,
                discord_bot=self._discord_bot,
            )
        except Exception as e:
            logging.warning(f"Failed to load Memory tool: {e}")

        # Load the primary tool if specified
        _primary_tool = None
        if _tool_selection_name and _tool_selection_name != "Memory":
            try:
                _primary_tool = importlib.import_module(
                    f"tools.{_tool_selection_name}"
                ).Tool(
                    method_send=self._discord_method_send,
                    discord_ctx=self._discord_ctx,
                    discord_bot=self._discord_bot,
                )
            except ModuleNotFoundError as e:
                logging.error(
                    "I cannot import the tool because the module is not found: %s", e
                )
                raise CustomErrorMessage(
                    "⚠️ The feature you've chosen is not available at the moment, please choose another tool using `/feature` command or try again later"
                )

        # Combine tool schemas
        _combined_schemas = []

        # Add Memory tool schema if available
        if _memory_tool:
            if type(_memory_tool.tool_schema_openai) == list:
                _combined_schemas.extend(_memory_tool.tool_schema_openai)
            else:
                _combined_schemas.append(_memory_tool.tool_schema_openai)

        # Add primary tool schema if available
        if _primary_tool:
            if _tool_selection_name == "CodeExecution":
                raise CustomErrorMessage(
                    "⚠️ Code execution is not supported in Pollinations.AI models, please use other models that support it."
                )
            else:
                if type(_primary_tool.tool_schema_openai) == list:
                    _combined_schemas.extend(_primary_tool.tool_schema_openai)
                else:
                    _combined_schemas.append(_primary_tool.tool_schema_openai)

        # Create final tool schema
        _tool_schema = _combined_schemas if _combined_schemas else None

        return {
            "tool_schema": _tool_schema,
            "tool_human_name": _primary_tool.tool_human_name
            if _primary_tool
            else (_memory_tool.tool_human_name if _memory_tool else None),
            "tool_object": _primary_tool if _primary_tool else _memory_tool,
        }

    @staticmethod
    def get_available_models():
        """Get available Pollinations.AI models"""
        try:
            # Text models
            text_response = requests.get(
                "https://text.pollinations.ai/models", timeout=10
            )
            text_models = (
                text_response.json() if text_response.status_code == 200 else []
            )

            # Image models
            image_response = requests.get(
                "https://image.pollinations.ai/models", timeout=10
            )
            image_models = (
                image_response.json() if image_response.status_code == 200 else []
            )

            return {"text_models": text_models, "image_models": image_models}
        except Exception as e:
            logging.error(f"Error fetching Pollinations.AI models: {e}")
            return {
                "text_models": ["openai", "mistral", "claude", "gemini"],
                "image_models": ["flux", "kontext", "sdxl"],
            }
