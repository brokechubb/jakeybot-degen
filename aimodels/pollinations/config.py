from core.exceptions import CustomErrorMessage
import importlib
import logging
import requests
import urllib.parse
from typing import Dict, List, Any


class ModelParams:
    def __init__(self):
        # Model provider thread
        self._model_provider_thread = "pollinations"

        # Default parameters for Pollinations.AI
        self._genai_params = {
            "temperature": 0.90,
            "top_p": 0.85,
            "model": "evil",  # Default text model - will be overridden by actual model name
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
    def get_available_models() -> Dict[str, Any]:
        """Get available Pollinations.AI models with enhanced information"""
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

            # Enhanced model categorization based on API documentation
            categorized_models = {
                "text_models": [],
                "image_models": [],
                "vision_models": [],
                "audio_models": [],
                "tts_voices": []
            }

            # Process text models
            if isinstance(text_models, list):
                categorized_models["text_models"] = [
                    model for model in text_models 
                    if model not in ["openai-audio", "openai-large", "claude-hybridspace"]
                ]
                # Add specialized models
                if "openai-audio" in text_models:
                    categorized_models["audio_models"].append("openai-audio")
                if "openai-large" in text_models:
                    categorized_models["vision_models"].append("openai-large")
                if "claude-hybridspace" in text_models:
                    categorized_models["vision_models"].append("claude-hybridspace")
            elif isinstance(text_models, dict):
                # Handle structured response
                categorized_models["text_models"] = list(text_models.keys())
                # Extract voices if available
                if "openai-audio" in text_models and "voices" in text_models["openai-audio"]:
                    categorized_models["tts_voices"] = text_models["openai-audio"]["voices"]

            # Process image models
            if isinstance(image_models, list):
                categorized_models["image_models"] = image_models
            elif isinstance(image_models, dict):
                categorized_models["image_models"] = list(image_models.keys())

            return categorized_models
        except Exception as e:
            logging.error(f"Error fetching Pollinations.AI models: {e}")
            # Return comprehensive fallback with all supported models
            return {
                "text_models": [
                    "evil", "unity", "mistral", "gemini", "openai", 
                    "openai-fast", "openai-roblox"
                ],
                "image_models": ["flux", "kontext", "sdxl"],
                "vision_models": ["openai-large", "claude-hybridspace", "openai"],
                "audio_models": ["openai-audio"],
                "tts_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            }
