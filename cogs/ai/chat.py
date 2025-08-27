from core.ai.core import ModelsList
from cogs.ai.generative_chat import BaseChat
from core.ai.history import History
from core.exceptions import *
from discord.commands import SlashCommandGroup
from discord.ext import commands
from os import environ
import logging
import discord
import inspect
import logging
import motor.motor_asyncio


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.author = environ.get("BOT_NAME", "Jakey Bot")

        # Use the shared database connection from the bot
        if hasattr(bot, "DBConn") and bot.DBConn is not None:
            self.DBConn: History = bot.DBConn
            logging.info("Chat cog using shared database connection")
        else:
            # Fallback: create our own connection if shared one is not available
            try:
                self.DBConn: History = History(
                    bot=bot,
                    db_conn=motor.motor_asyncio.AsyncIOMotorClient(
                        environ.get("MONGO_DB_URL")
                    ),
                )
                logging.info("Chat cog created fallback database connection")
            except Exception as e:
                logging.error(
                    f"Failed to initialize database connection in Chat cog: {e}"
                )
                raise e(
                    f"Failed to connect to MongoDB: {e}...\n\nPlease set MONGO_DB_URL in dev.env"
                )

        # Initialize the chat system
        self._ask_event = BaseChat(bot, self.author, self.DBConn)

    #######################################################
    # Pending request checker, prevents running multiple requests concurrently
    #######################################################
    async def _check_awaiting_response_in_progress(self, guild_id: int):
        if guild_id in self._ask_event.pending_ids:
            raise ConcurrentRequestError

    #######################################################
    # Event Listener: on_message
    #######################################################
    @commands.Cog.listener()
    async def on_message(self, message):
        await self._ask_event.on_message(message)

    #######################################################
    # Model Slash Command Group
    model = SlashCommandGroup(
        name="model", description="Configure default models for the conversation"
    )

    #######################################################
    # Slash Command Group: model.set
    #######################################################
    @model.command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "model",
        description="Choose default model for the conversation",
        choices=ModelsList.get_models_list(),
        required=True,
    )
    async def set(self, ctx, model: str):
        """Set the default model whenever you mention me!"""
        await ctx.response.defer(ephemeral=True)

        # Check if user has administrator permissions
        if ctx.guild and not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "❌ **Administrator permission required** to change the server's default model."
            )
            return

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if inference is in progress
        await self._check_awaiting_response_in_progress(guild_id)

        # Save the default model in the database
        await self.DBConn.set_default_model(guild_id=guild_id, model=model)

        # Validate model format
        if "::" not in model:
            await ctx.respond(
                "❌ Invalid model name, please choose a model from the list"
            )
            return
        else:
            _model = model.split("::")
            _model_provider = _model[0]
            _model_name = _model[-1]

        # if _model_provider != "gemini" and _model_provider != "claude":
        if not any(
            provider in _model_provider
            for provider in ["gemini", "claude", "openrouter", "openai", "kimi"]
        ):
            await ctx.respond(
                f"> This model lacks real time information and tools\n✅ Default model set to **{_model_name}** and chat history is set for provider **{_model_provider}**"
            )
        else:
            await ctx.respond(
                f"✅ Default model set to **{_model_name}** and chat history is set for provider **{_model_provider}**"
            )

    @set.error
    async def set_on_error(self, ctx: discord.ApplicationContext, error):
        _error = getattr(error, "original", error)

        if isinstance(_error, ConcurrentRequestError):
            await ctx.respond(
                "⚠️ Please wait until processing your previous request is completed before changing the model..."
            )
        elif isinstance(_error, discord.Forbidden):
            await ctx.respond(
                "❌ **Permission denied**. Administrator permission required to change the server's default model."
            )
        else:
            await ctx.respond("❌ Something went wrong, please try again later.")

        logging.error(
            "An error has occurred while executing models command, reason: ",
            exc_info=True,
        )

    #######################################################
    # Slash Command Group: model.list
    #######################################################
    @model.command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def list(self, ctx):
        """List all available models"""
        await ctx.response.defer(ephemeral=True)

        # Create an embed to list models
        _embed = discord.Embed(
            title="Available models",
            description=inspect.cleandoc(
                f"""Here are the list of available models that you can use

                You can set the default model for the conversation using `/model set` command or on demand through chat prompting
                via `@{self.bot.user.name} /model:model-name` command.
                
                Each provider has its own chat history, skills, and capabilities. Choose what's best for you.
                
                **Note**: Due to Discord's 25-choice limit, `/model set` shows priority models first. Use this list to see all available models."""
            ),
            color=discord.Color.random(),
        )

        # Group models by provider
        _model_provider_tabledict = {}
        async for _model in ModelsList.get_models_list_async():
            _model_provider = _model.split("::")[0]
            _model_name = _model.split("::")[-1]
            _model_provider_tabledict.setdefault(_model_provider, []).append(
                _model_name
            )

        # Add each provider and its models as a field in the embed
        for provider, models in _model_provider_tabledict.items():
            _embed.add_field(name=provider, value=", ".join(models), inline=False)

        await ctx.respond(embed=_embed)

    @list.error
    async def list_on_error(self, ctx: discord.ApplicationContext, error):
        await ctx.respond("❌ Something went wrong, please try again later.")
        logging.error(
            "An error has occurred while executing models command, reason: ",
            exc_info=True,
        )

    #######################################################
    # Slash Command Group: model.current
    #######################################################
    @model.command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def current(self, ctx):
        """Show the current default model for this server"""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        try:
            # Get the current default model from the database
            current_model = await self.DBConn.get_default_model(guild_id=guild_id)

            if current_model:
                # Parse the model to get provider and name
                if "::" in current_model:
                    _model = current_model.split("::")
                    _model_provider = _model[0]
                    _model_name = _model[-1]

                    # Create an embed to show current model
                    embed = discord.Embed(
                        title="🤖 Current Model",
                        description=f"**Server**: {ctx.guild.name if ctx.guild else 'DM'}\n**Provider**: {_model_provider}\n**Model**: {_model_name}",
                        color=discord.Color.green(),
                    )

                    # Add additional info based on provider
                    if _model_provider in [
                        "gemini",
                        "claude",
                        "openrouter",
                        "openai",
                        "kimi",
                    ]:
                        embed.add_field(
                            name="✅ Features",
                            value="• Real-time information\n• Tool support\n• Web search capabilities",
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name="⚠️ Features",
                            value="• Basic chat capabilities\n• Limited real-time information\n• No tool support",
                            inline=False,
                        )

                    embed.set_footer(text="Use /model set to change the model")

                    await ctx.respond(embed=embed)
                else:
                    await ctx.respond("❌ Invalid model format stored in database")
            else:
                # No model set, show default
                embed = discord.Embed(
                    title="🤖 Current Model",
                    description="**No model set** - Using system default\n\nUse `/model set` to choose a specific model",
                    color=discord.Color.blue(),
                )
                embed.set_footer(text="Default: Gemini 2.5 Flash")
                await ctx.respond(embed=embed)

        except Exception as e:
            logging.error(f"Error getting current model: {e}")
            await ctx.respond("❌ Error retrieving current model. Please try again.")

    @current.error
    async def current_on_error(self, ctx: discord.ApplicationContext, error):
        await ctx.respond("❌ Something went wrong, please try again later.")
        logging.error(
            "An error has occurred while executing model current command, reason: ",
            exc_info=True,
        )

    #######################################################
    # Slash Command: openrouter
    #######################################################
    @commands.slash_command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "model",
        description="Choose models at https://openrouter.ai/models. Syntax: provider/model-name",
        required=True,
    )
    async def openrouter(self, ctx, model: str):
        """Set the default OpenRouter model"""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if inference is in progress
        await self._check_awaiting_response_in_progress(guild_id)

        # Set the default OpenRouter model and clear the OpenRouter chat thread
        await self.DBConn.set_key(
            guild_id=guild_id, key="default_openrouter_model", value=model
        )
        _setkeymodel = await self.DBConn.get_key(
            guild_id=guild_id, key="default_openrouter_model"
        )
        await self.DBConn.set_key(
            guild_id=guild_id, key="chat_thread_openrouter", value=None
        )

        await ctx.respond(
            f"✅ Default OpenRouter model set to **{_setkeymodel}** and chat history for OpenRouter chats are cleared!\n"
            "To use this model, please set the model to OpenRouter using `/model set` command"
        )

    @openrouter.error
    async def openrouter_on_error(self, ctx: discord.ApplicationContext, error):
        _error = getattr(error, "original", error)

        if isinstance(_error, ConcurrentRequestError):
            await ctx.respond(
                "⚠️ Please wait until processing your previous request is completed before changing the OpenRouter model..."
            )
        else:
            await ctx.respond("❌ Something went wrong, please try again later.")
        logging.error(
            "An error has occurred while setting openrouter models, reason: ",
            exc_info=True,
        )

    #######################################################
    # Slash Command: sweep
    #######################################################
    @commands.slash_command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "reset_prefs",
        description="Clear the context history including the default model and feature settings",
    )
    async def sweep(self, ctx, reset_prefs: bool = False):
        """Clear the context history of the conversation"""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if inference is in progress
        await self._check_awaiting_response_in_progress(guild_id)

        # Command allowed only in DMs or in authorized guilds
        if ctx.guild is not None:
            if ctx.interaction.authorizing_integration_owners.guild is None:
                await ctx.respond(
                    "🚫 This command can only be used in DMs or authorized guilds!"
                )
                return

        # Save current settings before clearing history
        _feature = await self.DBConn.get_tool_config(guild_id=guild_id)
        _model = await self.DBConn.get_default_model(guild_id=guild_id)
        _openrouter_model = await self.DBConn.get_key(
            guild_id=guild_id, key="default_openrouter_model"
        )

        # Clear chat history
        await self.DBConn.clear_history(guild_id=guild_id)

        if not reset_prefs:
            # Restore settings if not resetting preferences
            await self.DBConn.set_tool_config(guild_id=guild_id, tool=_feature)
            await self.DBConn.set_default_model(guild_id=guild_id, model=_model)
            await self.DBConn.set_key(
                guild_id=guild_id,
                key="default_openrouter_model",
                value=_openrouter_model,
            )
            await ctx.respond("✅ Chat history reset!")
        else:
            await ctx.respond(
                "✅ Chat history reset, model and feature settings are cleared!"
            )

    @sweep.error
    async def sweep_on_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        _error = getattr(error, "original", error)
        if isinstance(_error, PermissionError):
            await ctx.respond(
                "⚠️ An error has occurred while clearing chat history, logged the error to the owner"
            )
        elif isinstance(_error, FileNotFoundError):
            await ctx.respond("ℹ️ Chat history is already cleared!")
        elif isinstance(_error, ConcurrentRequestError):
            await ctx.respond(
                "⚠️ Please wait until processing your previous request is completed before clearing the chat history..."
            )
        else:
            await ctx.respond("❌ Something went wrong, please try again later.")
            logging.error(
                "An error has occurred while executing sweep command, reason: ",
                exc_info=True,
            )

    #######################################################
    # Slash Command: feature
    #######################################################
    @commands.slash_command(
        name="feature",
        description="Integrate tools to chat! Setting chat features will clear your history!",
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option(
        "capability",
        description="Integrate tools to chat! Setting chat features will clear your history!",
        choices=ModelsList.get_tools_list(),
    )
    async def feature(self, ctx, capability: str):
        """Enhance your chat with capabilities! Some are in BETA so things may not always pick up"""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Check if inference is in progress
        await self._check_awaiting_response_in_progress(guild_id)

        # Command allowed only in DMs or in authorized guilds
        if ctx.guild is not None:
            if ctx.interaction.authorizing_integration_owners.guild is None:
                await ctx.respond(
                    "🚫 This command can only be used in DMs or authorized guilds!"
                )
                return

        # Retrieve current settings
        _cur_feature = await self.DBConn.get_tool_config(guild_id=guild_id)
        _model = await self.DBConn.get_default_model(guild_id=guild_id)
        _openrouter_model = await self.DBConn.get_key(
            guild_id=guild_id, key="default_openrouter_model"
        )

        # Convert "disabled" to None
        if capability == "disabled":
            capability = None

        if _cur_feature == capability:
            await ctx.respond("✅ Feature already set!")
        else:
            # Clear chat history IF the feature is not set to None
            if _cur_feature:
                await self.DBConn.clear_history(guild_id=guild_id)

            # Set new capability and restore default model
            await self.DBConn.set_tool_config(guild_id=guild_id, tool=capability)
            await self.DBConn.set_default_model(guild_id=guild_id, model=_model)
            await self.DBConn.set_key(
                guild_id=guild_id,
                key="default_openrouter_model",
                value=_openrouter_model,
            )

            # Use AutoReturnManager if available and capability is not None
            if (
                capability is not None
                and hasattr(self.bot, "auto_return_manager")
                and self.bot.auto_return_manager
            ):
                try:
                    # Switch tool with timeout using AutoReturnManager
                    await self.bot.auto_return_manager.switch_tool_with_timeout(
                        guild_id=guild_id, new_tool=capability, user_id=ctx.author.id
                    )

                    # Get timeout for this tool
                    timeout = self.bot.auto_return_manager.tool_timeouts.get(
                        capability,
                        self.bot.auto_return_manager.tool_timeouts["default"],
                    )
                    timeout_minutes = timeout // 60
                    timeout_seconds = timeout % 60

                    if timeout_minutes > 0:
                        timeout_str = (
                            f"{timeout_minutes}m {timeout_seconds}s"
                            if timeout_seconds > 0
                            else f"{timeout_minutes}m"
                        )
                    else:
                        timeout_str = f"{timeout_seconds}s"

                    # Get smart suggestions for the new tool
                    suggestions = (
                        await self.bot.auto_return_manager.get_smart_suggestions(
                            guild_id, f"switched to {capability}"
                        )
                    )

                    # Build response with suggestions
                    response_parts = []

                    if not _cur_feature:
                        response_parts.append(
                            f"✅ Feature **{capability}** enabled successfully!"
                        )
                    else:
                        response_parts.append(
                            f"✅ Feature **{capability}** enabled successfully and chat is reset!"
                        )

                    response_parts.append(
                        f"⏰ Will automatically return to {self.bot.auto_return_manager.default_tool} in {timeout_str}"
                    )

                    # Add smart suggestions if available
                    if suggestions:
                        response_parts.append("\n🧠 **Smart Suggestions:**")
                        for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                            response_parts.append(f"• {suggestion}")

                        if len(suggestions) > 3:
                            response_parts.append(
                                f"• ... and {len(suggestions) - 3} more suggestions"
                            )

                    # Add helpful tips
                    response_parts.append(f"\n💡 **Quick Actions:**")
                    response_parts.append(f"• `/timeout_status` - Check remaining time")
                    response_parts.append(f"• `/extend_timeout <time>` - Add more time")
                    response_parts.append(f"• `/return_to_default` - Switch back now")
                    response_parts.append(f"• `/smart_suggestions` - Get more tips")

                    await ctx.respond("\n".join(response_parts))

                except Exception as e:
                    logging.error(f"Error using AutoReturnManager: {e}")
                    # Fall back to normal response
                    if not _cur_feature:
                        await ctx.respond(
                            f"✅ Feature **{capability}** enabled successfully"
                        )
                    else:
                        await ctx.respond(
                            f"✅ Feature **{capability}** enabled successfully and chat is reset to reflect the changes"
                        )
            else:
                # Normal response without auto-return
                if capability is None:
                    await ctx.respond(
                        "✅ Features disabled and chat is reset to reflect the changes"
                    )
                else:
                    if not _cur_feature:
                        await ctx.respond(
                            f"✅ Feature **{capability}** enabled successfully"
                        )
                    else:
                        await ctx.respond(
                            f"✅ Feature **{capability}** enabled successfully and chat is reset to reflect the changes"
                        )

    @feature.error
    async def feature_on_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        _error = getattr(error, "original", error)

        if isinstance(_error, ConcurrentRequestError):
            await ctx.respond(
                "⚠️ Please wait until processing your previous request is completed before changing agents..."
            )
        else:
            await ctx.respond("❌ Something went wrong, please try again later.")
        logging.error(
            "An error has occurred while executing feature command, reason: ",
            exc_info=True,
        )

    ####################################################################################
    # Knowledge Management Commands
    ####################################################################################

    @commands.slash_command(
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
        },
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    @discord.option("fact", description="The fact to remember", required=True)
    @discord.option(
        "expires_in", description="Expiration time (e.g., 1d, 2h, 30m)", required=False
    )
    async def remember(self, ctx, fact: str, expires_in: str = None):
        """Remember a piece of information"""
        await ctx.response.defer(ephemeral=True)

        # Determine guild/user based on SHARED_CHAT_HISTORY setting
        if environ.get("SHARED_CHAT_HISTORY", "false").lower() == "true":
            guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        else:
            guild_id = ctx.author.id

        # Get username for prepending to fact
        username = ctx.author.display_name or f"User{ctx.author.id}"

        # Prepend username to fact text to associate information with specific user
        fact_with_user = f"[{username}] {fact}"

        # Parse expiration time
        expires_at = None
        if expires_in:
            try:
                from datetime import datetime, timedelta, timezone

                now = datetime.now(timezone.utc)
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
                await ctx.respond(
                    "⚠️ Invalid expiration format. Use number followed by d, h, or m (e.g., 1d, 2h, 30m)"
                )
                return

        try:
            fact_id = await self.DBConn.add_fact(
                guild_id,
                ctx.author.id,
                fact_with_user,
                source=f"user_command/{ctx.author.id}",
                expires_at=expires_at,
            )
            response = f"✅ I'll remember that (Fact ID: {fact_id})"
            if expires_at:
                response += f"\n⏰ Expires: {expires_at.strftime('%Y-%m-%d %H:%M')} UTC"
            await ctx.respond(response)
        except Exception as e:
            await ctx.respond(f"❌ Failed to remember: {str(e)}")
            logging.error("Error remembering fact: %s", e)


def setup(bot):
    bot.add_cog(Chat(bot))
