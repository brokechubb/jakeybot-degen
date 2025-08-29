from .manifest import ToolManifest
from os import environ
import datetime
import discord
import aiohttp
import io
import urllib.parse
import logging


class Tool(ToolManifest):
    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

    # Image generator using Pollinations.AI
    async def _tool_function(self, prompt: str, url_context: list[str] = None):
        # Create image
        _message_current = await self.method_send(
            f"⌛ Generating with prompt **{prompt}** using Pollinations.AI... this may take a few minutes"
        )

        # Check if global aiohttp client session is initialized
        if not hasattr(self.discord_bot, "_aiohttp_main_client_session"):
            raise Exception(
                "aiohttp client session for get requests not initialized, please check the bot configuration"
            )

        # Check if POLLINATIONS_API_KEY is set (optional but recommended)
        api_key = environ.get("POLLINATIONS_API_KEY")
        if api_key:
            logging.info("Using Pollinations.AI with API key for premium features")
        else:
            logging.info("Using Pollinations.AI anonymous tier")

        try:
            # Generate image using Pollinations.AI
            image_url = await self._generate_pollinations_image(
                prompt, url_context, api_key
            )

            # Download and send the image
            _msgID = await self._download_and_send_image(image_url)

            # Delete status message
            await _message_current.delete()

            return {
                "guidelines": "The image is already sent to the UI, no need to print the URLs as it will just cause previews to display images twice.",
                "context_results": [image_url],
                "status": "Image generated successfully using Pollinations.AI",
            }

        except Exception as e:
            # Delete status message on error
            await _message_current.delete()
            raise e

    async def _generate_pollinations_image(
        self, prompt: str, url_context: list[str] = None, api_key: str = None
    ) -> str:
        """Generate image using Pollinations.AI API"""

        # Available Pollinations.AI image models
        available_models = ["flux", "kontext", "sdxl"]

        # Default parameters
        params = {
            "width": 1024,
            "height": 1024,
            "private": "true",  # Set private to true as requested
        }

        # Add API key if available
        if api_key:
            params["token"] = api_key
            # Remove logo for authenticated users
            params["nologo"] = "true"

        # Add image URL for image-to-image generation if available
        if url_context and len(url_context) > 0:
            params["image"] = url_context[0]
            # Use kontext model for image-to-image
            model = "kontext"
        else:
            # Use flux model for text-to-image
            model = "flux"

        # Set model parameter
        params["model"] = model

        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(prompt)

        # Construct the Pollinations.AI URL
        base_url = "https://image.pollinations.ai"
        url = f"{base_url}/prompt/{encoded_prompt}"

        # Create aiohttp session with timeout
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    # For Pollinations.AI, the response URL is the generated image
                    return url
                else:
                    error_text = await response.text()
                    logging.error(
                        f"Pollinations.AI image API error: {response.status} - {error_text}"
                    )
                    raise Exception(
                        f"❌ Failed to generate image: HTTP {response.status}"
                    )

    async def _download_and_send_image(self, image_url: str) -> discord.Message:
        """Download image from URL and send it to Discord"""

        # Download the image
        async with self.discord_bot._aiohttp_main_client_session.get(
            image_url
        ) as response:
            if response.status == 200:
                _image_data = await response.read()

                # Send the image
                _msgID = await self.method_send(
                    file=discord.File(
                        fp=io.BytesIO(_image_data),
                        filename=f"pollinations_generated_{datetime.datetime.now().strftime('%H_%M_%S_%m%d%Y_%s')}.png",
                    )
                )
                return _msgID
            else:
                raise Exception(
                    f"❌ Failed to download image from {image_url}, status code: {response.status}"
                )
