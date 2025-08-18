from .manifest import ToolManifest
import discord
import io


class Tool(ToolManifest):
    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

    async def _tool_function_canvas(
        self,
        thread_title: str,
        plan: str,
        content: str,
        code: str = None,
        todos: list = None,
    ):
        # Check if we're in a server
        if not self.discord_ctx.guild:
            raise Exception("This tool can only be used in a server")

        # Create a new thread
        _msgstarter = await self.discord_ctx.channel.send(
            f"📃 Planning **{thread_title}**"
        )
        _thread = await _msgstarter.create_thread(
            name=thread_title, auto_archive_duration=1440
        )

        # Send the plan
        # Encode and decode using bytes and later decode it again using string escape
        await _thread.send(f"**Plan:**\n{plan}")
        # Send the content
        await _thread.send(f"**Content:**\n{content}")
        # Send the code if available
        if code:
            await _thread.send(f"**Code:**\n```{code}```")
        # Send the todos if available
        if todos:
            await _thread.send("**Todos:**\n")
            for _todo in todos:
                await _thread.send(f"- {_todo}")

        return "Thread created successfully"

    async def _tool_function_artifacts(self, file_contents: str, file_name: str):
        """Create an artifact from the given contents and upload it as a file
        attachment.

        Discord expects *binary* file-like objects.  Using ``io.StringIO`` will
        yield a text stream and causes a runtime error in `discord.File`.  We
        therefore encode the text into UTF-8 bytes and wrap it with
        ``io.BytesIO``.
        """

        # Encode content to bytes and wrap with BytesIO for Discord upload
        bytes_buffer = io.BytesIO(file_contents.encode("utf-8"))

        # Reset pointer to the start just in case
        bytes_buffer.seek(0)

        await self.method_send(file=discord.File(bytes_buffer, file_name))

        return f"Artifact {file_name} created successfully"

    # ------------------------------------------------------------------
    # Compatibility alias / dispatcher
    # ------------------------------------------------------------------
    async def _tool_function(self, **kwargs):
        """Generic dispatcher to maintain backwards compatibility.

        The Gemini agent may sometimes call this tool via the generic
        ``_tool_function`` attribute instead of the more specific
        ``_tool_function_<name>``. Determine which concrete method to invoke
        based on the supplied keyword arguments.
        """

        if "thread_title" in kwargs and "plan" in kwargs and "content" in kwargs:
            return await self._tool_function_canvas(**kwargs)
        elif "file_contents" in kwargs and "file_name" in kwargs:
            return await self._tool_function_artifacts(**kwargs)
        else:
            raise ValueError(
                "Unable to determine which ideation sub-tool to execute from provided arguments"
            )
