import logging
from azure.storage.blob.aio import BlobServiceClient
from discord.ext import bridge
from os import environ
import aiohttp
import logging
import openai


# List of services to be started, separated from main.py
# for cleanliness and modularity
class ServicesInitBot(bridge.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start_services(self):

        # OpenAI client for openai models
        _base_url = environ.get("OPENAI_API_ENDPOINT")
        _openai_api_key = environ.get("OPENAI_API_KEY")

        # Initialize OpenAI client only if API key is provided
        if _openai_api_key:
            # Check if we need to use default_query param for Azure OpenAI
            _default_query = (
                {"api-version": "preview"}
                if environ.get("OPENAI_USE_AZURE_OPENAI") and _base_url
                else None
            )
            self._openai_client = openai.AsyncOpenAI(
                api_key=_openai_api_key,
                base_url=_base_url,
                default_query=_default_query,
            )
            logging.info(
                "OpenAI client initialized successfully %s",
                f"with custom endpoint: {_base_url}"
                if _base_url
                else "with default endpoint",
            )
        else:
            self._openai_client = None
            logging.warning("OPENAI_API_KEY not set; OpenAI models disabled.")

        # We are currently testing the next generation of Azure OpenAI
        # Simply pass this to your baseURL: https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/
        # If things break, enable the commented code below to use Azure OpenAI without the nextgen API
        # and comment the above line

        # if environ.get("OPENAI_USE_AZURE_OPENAI"):
        #     # OpenAI API endpoint must be set to Azure OpenAI endpoint
        #     if not _base_url:
        #         raise ValueError("OPENAI_API_ENDPOINT must be set when using Azure OpenAI")
        #
        #     self._openai_client = openai.AsyncAzureOpenAI(
        #         azure_endpoint=_base_url,
        #         api_key=environ.get("OPENAI_API_KEY"),
        #         api_version="2024-12-01-preview"
        #     )
        #     logging.info("Using Azure OpenAI service for serving OpenAI models")
        # else:
        #     self._openai_client = openai.AsyncOpenAI(
        #         api_key=environ.get("OPENAI_API_KEY"),
        #         base_url=_base_url
        #     )
        #     logging.info("Using OpenAI API for serving OpenAI models")

        # OpenAI client for Groq based models
        if environ.get("GROQ_API_KEY"):
            self._openai_client_groq = openai.AsyncOpenAI(
                api_key=environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            )
            logging.info("OpenAI client for Groq initialized successfully")
        else:
            self._openai_client_groq = None
            logging.warning("GROQ_API_KEY not set; Groq models disabled.")

        # Everything else (mostly GET requests)
        self._aiohttp_main_client_session = aiohttp.ClientSession(loop=self.loop)
        logging.info("aiohttp client session initialized successfully")

        # Azure Blob Storage Client
        try:
            azure_account_url = environ.get("AZURE_STORAGE_ACCOUNT_URL")
            azure_connection_string = environ.get("AZURE_STORAGE_CONNECTION_STRING")
            
            # Only initialize if both credentials are provided
            if azure_account_url and azure_connection_string:
                self._azure_blob_service_client = BlobServiceClient(
                    account_url=azure_account_url
                ).from_connection_string(azure_connection_string)
                logging.info("Azure Blob Storage client initialized successfully")
            else:
                self._azure_blob_service_client = None
                if not azure_account_url and not azure_connection_string:
                    logging.info("Azure Blob Storage not configured - skipping initialization")
                else:
                    logging.warning("Azure Blob Storage partially configured - both AZURE_STORAGE_ACCOUNT_URL and AZURE_STORAGE_CONNECTION_STRING required")
        except Exception as e:
            logging.error(
                "Failed to initialize Azure Blob Storage client: %s, skipping....", e
            )
            self._azure_blob_service_client = None

    async def stop_services(self):
        # Close aiohttp client sessions
        await self._aiohttp_main_client_session.close()
        logging.info("aiohttp client session closed successfully")

        # Close Azure Blob Storage client
        if hasattr(self, "_azure_blob_service_client") and self._azure_blob_service_client is not None:
            try:
                await self._azure_blob_service_client.close()
                logging.info("Azure Blob Storage client closed successfully")
            except Exception as e:
                logging.error("Failed to close Azure Blob Storage client: %s", e)
