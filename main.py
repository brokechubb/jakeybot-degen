from core.services.initbot import ServicesInitBot
import logging
import logging.config

# Setup colored logging
try:
    from core.services.colored_logging import setup_colored_logging

    setup_colored_logging(
        level=logging.INFO,
        use_simple=False,  # Use advanced colored formatter
    )
    logging.info("🎨 Colored logging initialized successfully")
except ImportError:
    # Fallback to standard logging if colored logging is not available
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(levelname)s %(asctime)s [%(pathname)s:%(lineno)d - %(module)s.%(funcName)s()]:\n%(message)s",
                "datefmt": "%m/%d/%Y %I:%M:%S %p",
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {"": {"handlers": ["default"], "level": "INFO", "propagate": False}},
    }

    logging.config.dictConfig(logging_config)
    logging.warning("Colored logging not available, using standard logging")

from discord.ext import commands
from inspect import cleandoc
from os import chdir, mkdir, environ
from pathlib import Path
import aiofiles.os
import discord
import dotenv
import logging
import re
import socket
import yaml
import motor.motor_asyncio
from core.ai.history import History
from core.services.auto_return_manager import AutoReturnManager
import google.generativeai as genai  # Import Gemini API client

# Go to project root directory
chdir(Path(__file__).parent.resolve())

# Load environment variables
dotenv.load_dotenv("dev.env")

# Validate configuration
try:
    from core.services.config_validator import (
        validate_configuration,
        get_config_summary,
    )

    validate_configuration()

    # Log configuration summary
    config_summary = get_config_summary()
    try:
        from core.services.colored_logging import log_success, log_info

        log_success("Configuration validated successfully")
        log_info(
            f"Bot: {config_summary['bot_name']} (prefix: {config_summary['bot_prefix']})"
        )
        log_info(
            f"AI Providers: {len(config_summary['ai_providers_configured'])} configured"
        )
        log_info(
            f"Database: {'Configured' if config_summary['database_configured'] else 'Not configured'}"
        )
    except ImportError:
        logging.info(f"Configuration validated successfully")
        logging.info(
            f"Bot: {config_summary['bot_name']} (prefix: {config_summary['bot_prefix']})"
        )
        logging.info(
            f"AI Providers: {len(config_summary['ai_providers_configured'])} configured"
        )
        logging.info(
            f"Database: {'Configured' if config_summary['database_configured'] else 'Not configured'}"
        )

except ImportError:
    logging.warning("Configuration validator not available, skipping validation")
except Exception as e:
    logging.error(f"Configuration validation failed: {e}")
    raise

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# Subclass this bot
class InitBot(ServicesInitBot):
    def __init__(self, *args, **kwargs):
        # Create socket instance and bind socket to 45769
        self._lock_socket_instance(45769)

        super().__init__(*args, **kwargs)

        # Prepare temporary directory
        if environ.get("TEMP_DIR") is not None:
            if Path(environ.get("TEMP_DIR")).exists():
                for file in Path(environ.get("TEMP_DIR", "temp")).iterdir():
                    file.unlink()
            else:
                mkdir(environ.get("TEMP_DIR"))
        else:
            environ["TEMP_DIR"] = "temp"
            mkdir(environ.get("TEMP_DIR"))

        # Initialize non-async services
        try:
            self.auto_return_manager = AutoReturnManager(self)
            logging.info("AutoReturnManager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize AutoReturnManager: {e}")
            self.auto_return_manager = None

        try:
            from core.services.input_validator import get_input_validator

            self.input_validator = get_input_validator()
            logging.info("Input validator initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize input validator: {e}")
            self.input_validator = None

        # Configure Gemini API client globally
        try:
            gemini_api_key = environ.get("GEMINI_API_KEY")
            gemini_api_key_status = "set" if gemini_api_key else "not set"
            logging.info(
                f"GEMINI_API_KEY status during initialization: {gemini_api_key_status}"
            )

            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self._gemini_api_configured = True
                logging.info("Gemini API configured successfully")
            else:
                self._gemini_api_configured = False
                logging.warning(
                    "GEMINI_API_KEY not set; Gemini API will not be available for dynamic question generation."
                )
        except Exception as e:
            logging.error(f"Failed to configure Gemini API: {e}")
            self._gemini_api_configured = False

        # Initialize async services after bot is ready
        self.loop.create_task(self._initialize_async_services())
        self.loop.create_task(self.start_services())
        logging.info("Services initialization started")

        # Initialize non-async performance services
        try:
            from core.services.cache_manager import get_cache_manager

            self.cache_manager = get_cache_manager()
            logging.info("Cache manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize cache manager: {e}")
            self.cache_manager = None

    async def _initialize_async_services(self):
        """Initialize async services that require await."""
        # Initialize shared database connection
        try:
            from core.services.database_manager import get_database_manager

            db_manager = await get_database_manager()
            db_client = await db_manager.get_client()

            self.DBConn = History(
                bot=self,
                db_conn=db_client,
            )
            logging.info("Shared database connection initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize shared database connection: {e}")
            self.DBConn = None

        # Initialize Rate Limiter
        try:
            from core.services.rate_limiter import get_rate_limiter

            self.rate_limiter = await get_rate_limiter()
            logging.info("Rate limiter initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize rate limiter: {e}")
            self.rate_limiter = None

        # Initialize async performance services
        try:
            from core.services.performance_monitor import get_performance_monitor

            self.performance_monitor = await get_performance_monitor()
            logging.info("Performance monitor initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize performance monitor: {e}")
            self.performance_monitor = None

        try:
            from core.services.connection_pool import get_connection_pool

            self.connection_pool = await get_connection_pool()
            logging.info("Connection pool manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize connection pool manager: {e}")
            self.connection_pool = None

    def _lock_socket_instance(self, port):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind(("localhost", port))
            logging.info("Socket bound to port %s", port)
        except socket.error as e:
            logging.error("Failed to bind socket port: %s, reason: %s", port, str(e))
            raise e

    # Shutdown the bot
    async def close(self):
        # Close services
        await self.stop_services()
        logging.info("Services stopped successfully")

        # Cleanup AutoReturnManager
        if hasattr(self, "auto_return_manager") and self.auto_return_manager:
            await self.auto_return_manager.cleanup()
            logging.info("AutoReturnManager cleanup completed")

        # Cleanup database connection
        try:
            from core.services.database_manager import cleanup_database

            await cleanup_database()
            logging.info("Database connection cleanup completed")
        except Exception as e:
            logging.error(f"Failed to cleanup database connection: {e}")

        # Cleanup performance services
        try:
            from core.services.performance_monitor import cleanup_performance_monitor

            await cleanup_performance_monitor()
            logging.info("Performance monitor cleanup completed")
        except Exception as e:
            logging.error(f"Failed to cleanup performance monitor: {e}")

        try:
            from core.services.cache_manager import cleanup_cache

            await cleanup_cache()
            logging.info("Cache manager cleanup completed")
        except Exception as e:
            logging.error(f"Failed to cleanup cache manager: {e}")

        try:
            from core.services.connection_pool import cleanup_connection_pool

            await cleanup_connection_pool()
            logging.info("Connection pool manager cleanup completed")
        except Exception as e:
            logging.error(f"Failed to cleanup connection pool manager: {e}")

        # Cleanup rate limiter
        try:
            from core.services.rate_limiter import cleanup_rate_limiter

            await cleanup_rate_limiter()
            logging.info("Rate limiter cleanup completed")
        except Exception as e:
            logging.error(f"Failed to cleanup rate limiter: {e}")

        # Remove temp files
        if Path(environ.get("TEMP_DIR", "temp")).exists():
            for file in Path(environ.get("TEMP_DIR", "temp")).iterdir():
                await aiofiles.os.remove(file)

        # Close socket
        self._socket.close()

        await super().close()


bot = InitBot(command_prefix=environ.get("BOT_PREFIX", "$"), intents=intents)


###############################################
# ON READY
###############################################
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game("Preparing the bot for it's first use...")
    )
    # https://stackoverflow.com/a/65780398 - for multiple statuses
    await bot.change_presence(
        activity=discord.Game(f"/ask me anything or {bot.command_prefix}help")
    )
    try:
        from core.services.colored_logging import log_success

        log_success(f"{bot.user} is ready and online!")
    except ImportError:
        logging.info("%s is ready and online!", bot.user)


###############################################
# ON USER MESSAGE
###############################################
@bot.event
async def on_message(message: discord.Message):
    # https://discord.com/channels/881207955029110855/1146373275669241958
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    # Check if the bot was only mentioned without any content or image attachments
    # On generative ask command, the same logic is used but it will just invoke return and the bot will respond with this
    if (
        bot.user.mentioned_in(message)
        and not message.attachments
        and not re.sub(f"<@{bot.user.id}>", "", message.content).strip()
    ):
        await message.channel.send(
            cleandoc(f"""Yo <@{message.author.id}> – **{bot.user.name}** in the house 💀✨

                    You pinged me, so what’s good?
                    
                    • Wanna pick my brain? Just **/ask** or @ me with your question – I spit answers faster than a memecoin rug-pull.
                    • Commands? Smash **/** and scroll, or `{bot.command_prefix}help` if you’re feeling 2016.

                    Examples:
                    • “@{bot.user.name} how many R’s in strawberry?”
                    • **/ask** prompt: “tell me a joke (make it dark)”
                    • “yo @{bot.user.name} hit me with today’s motivation.”

                    Now quit reading and gamble your questions on me 🔥""")
        )


with open("commands.yaml", "r") as file:
    cog_commands = yaml.safe_load(file)
    for command in cog_commands:
        try:
            bot.load_extension(f"cogs.{command}")
        except Exception as e:
            logging.error(
                "cogs.%s failed to load, skipping... The following error of the cog: %s",
                command,
                e,
            )
            continue


# Initialize custom help
class CustomHelp(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Misc"

    # Override "get_opening_note" with custom implementation
    def get_opening_note(self):
        """Returns help command's opening note. This is mainly useful to override for i18n purposes.

        The default implementation returns ::

            Use `{prefix}{command_name} [command]` for more info on a command.
            You can also use `{prefix}{command_name} [category]` for more info on a category.

        Returns
        -------
        :class:`str`
            The help command opening note.
        """
        command_name = self.invoked_with
        return cleandoc(f"""**{bot.user.name}** Help & Commands

                🚀 **Quick Start**: Use `/help` or `/quickstart` for the full guide!
                
                📋 **Core Commands**:
                • `/ask <question>` - Ask Jakey anything
                • `/model set <model>` - Switch AI models  
                • `/feature <tool>` - Enable tools (Memory, CryptoPrice, etc.)
                • `/sweep` - Clear conversation history
                
                🛠️ **Available Tools**:
                • **Memory** - Remember and recall information
                • **CryptoPrice** - Live token prices
                • **CurrencyConverter** - Currency conversion
                • **YouTube** - Video analysis
                • **GitHub** - Code repository access
                
                💡 **Pro Tips**:
                • Start with `/feature Memory` for best experience
                • Use natural language - Jakey understands context
                • Set reminders with `/remind <time> <message>`
                
                📚 **More Help**:
                Use `{self.context.clean_prefix}{command_name} [command]` for detailed command info
                Use `{self.context.clean_prefix}{command_name} [category]` for category info""")

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=discord.Color.random())
            await destination.send(embed=embed)


bot.help_command = CustomHelp()

bot.run(environ.get("TOKEN"))
