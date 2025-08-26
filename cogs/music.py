import logging
import discord
from discord.ext import commands
import wavelink
from typing import Optional, List
import asyncio
from datetime import datetime, timedelta
from os import environ


class MusicPlayer(wavelink.Player):
    """Custom music player with queue management and enhanced features."""

    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.custom_queue: List[wavelink.Playable] = []
        self.current_track: Optional[wavelink.Playable] = None
        self.loop_mode: str = "none"  # none, single, queue
        self._volume: int = 50
        self.last_activity: datetime = datetime.now()
        self.skip_votes: set = set()
        self.required_votes: int = 3

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int):
        self._volume = value

    @property
    def connected(self) -> bool:
        """Check if the player is connected to a voice channel."""
        return hasattr(self, "channel") and self.channel is not None

    async def add_track(self, track: wavelink.Playable) -> None:
        """Add a track to the queue."""
        if not isinstance(track, wavelink.Playable):
            logging.error(f"Attempted to add non-Playable to queue: {type(track)}")
            return
        self.custom_queue.append(track)

    async def get_next_track(self) -> Optional[wavelink.Playable]:
        """Get the next track from the queue."""
        if not self.custom_queue:
            return None

        track = self.custom_queue.pop(0)
        logging.info(
            f"Getting next track: {track.title if hasattr(track, 'title') else track} (type: {type(track)})"
        )

        if not isinstance(track, wavelink.Playable):
            logging.error(f"Queue contained non-Playable object: {type(track)}")
            return None

        self.current_track = track
        return track

    async def clear_queue(self) -> None:
        """Clear the music queue."""
        self.custom_queue.clear()

    async def remove_track(self, index: int) -> Optional[wavelink.Playable]:
        """Remove a track from the queue by index."""
        if 0 <= index < len(self.custom_queue):
            return self.custom_queue.pop(index)
        return None

    async def shuffle_queue(self) -> None:
        """Shuffle the music queue."""
        import random

        random.shuffle(self.custom_queue)

    async def get_queue_info(self) -> str:
        """Get formatted queue information."""
        if not self.custom_queue:
            return "🎵 **Queue is empty**"

        queue_info = f"🎵 **Music Queue** ({len(self.custom_queue)} tracks)\n\n"

        for i, track in enumerate(self.custom_queue[:10], 1):  # Show first 10 tracks
            duration = str(timedelta(seconds=int(track.length)))
            queue_info += f"**{i}.** {track.title} - `{duration}`\n"

        if len(self.custom_queue) > 10:
            queue_info += f"\n... and {len(self.custom_queue) - 10} more tracks"

        return queue_info


class Music(commands.Cog):
    """Music commands for JakeyBot with LavaLink v4 support."""

    def __init__(self, bot):
        self.bot = bot
        self.players: dict = {}  # guild_id -> MusicPlayer
        self.lavalink_enabled = (
            environ.get("LAVALINK_V4_ENABLED", "false").lower() == "true"
        )
        self.voice_enabled = (
            environ.get("ENABLE_VOICE_FEATURES", "false").lower() == "true"
        )

        if self.lavalink_enabled and self.voice_enabled:
            self.bot.loop.create_task(self.connect_nodes())
            self.bot.loop.create_task(self.queue_monitor())
            logging.info("Music cog initialized with LavaLink v4 support")
        else:
            logging.info("Music cog initialized (LavaLink disabled)")

    async def connect_nodes(self):
        """Connect to LavaLink nodes."""
        await self.bot.wait_until_ready()

        try:
            node: wavelink.Node = wavelink.Node(
                uri=environ.get("ENV_LAVALINK_URI", "http://127.0.0.1:2333"),
                password=environ.get("ENV_LAVALINK_PASS", "youshallnotpass"),
                retries=3,
            )

            await wavelink.Pool.connect(nodes=[node], client=self.bot)
            logging.info("Connected to LavaLink v4 node successfully")

        except Exception as e:
            logging.error(f"Failed to connect to LavaLink node: {e}")

    async def queue_monitor(self):
        """Monitor queues and ensure tracks continue playing."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                for guild_id, player in self.players.items():
                    # Check if player is connected but not playing and has tracks in queue
                    if (
                        player.connected
                        and not player.playing
                        and len(player.custom_queue) > 0
                    ):
                        logging.info(
                            f"Queue monitor: Player not playing but has {len(player.custom_queue)} tracks in queue"
                        )

                        # Try to play the next track
                        next_track = await player.get_next_track()
                        if isinstance(next_track, wavelink.Playable):
                            try:
                                await player.play(next_track)
                                logging.info(
                                    f"Queue monitor: Started playing {next_track.title}"
                                )
                            except Exception as e:
                                logging.error(
                                    f"Queue monitor: Failed to play {next_track.title}: {e}"
                                )
                                # Put the track back in the queue
                                await player.add_track(next_track)

                # Check every 10 seconds
                await asyncio.sleep(10)

            except Exception as e:
                logging.error(f"Error in queue monitor: {e}")
                await asyncio.sleep(10)

    def get_player(self, guild_id: int) -> Optional[MusicPlayer]:
        """Get a music player for a guild."""
        return self.players.get(guild_id)

    async def ensure_voice(self, ctx) -> Optional[MusicPlayer]:
        """Ensure the bot is in a voice channel and return the player."""
        if not ctx.author.voice:
            await ctx.followup.send(
                "❌ You need to be in a voice channel to use music commands!",
                ephemeral=True,
            )
            return None

        if not ctx.voice_client:
            try:
                # Connect to voice channel and create player
                voice_client = await ctx.author.voice.channel.connect(cls=MusicPlayer)
                self.players[ctx.guild.id] = voice_client
                await ctx.followup.send(
                    f"🎵 **Joined** {ctx.author.voice.channel.name}"
                )
                return voice_client
            except Exception as e:
                await ctx.followup.send(
                    f"❌ Failed to join voice channel: {e}", ephemeral=True
                )
                return None
        else:
            # Bot is already in a voice channel
            # Ensure the connected voice client is our custom MusicPlayer
            if not isinstance(ctx.voice_client, MusicPlayer):
                try:
                    existing_channel = ctx.voice_client.channel
                    await ctx.voice_client.disconnect()
                    voice_client = await existing_channel.connect(cls=MusicPlayer)
                    self.players[ctx.guild.id] = voice_client
                    await ctx.followup.send(
                        "🔁 Reinitialized voice player for this guild"
                    )
                    return voice_client
                except Exception as e:
                    await ctx.followup.send(
                        f"❌ Failed to reinitialize voice player: {e}",
                        ephemeral=True,
                    )
                    return None

            player = self.get_player(ctx.guild.id)
            if not player:
                # Store the existing voice client as player
                self.players[ctx.guild.id] = ctx.voice_client
                return ctx.voice_client
            return player

    @commands.slash_command(
        name="play",
        description="Play music from YouTube, Spotify, or other sources",
        guild_ids=None,
    )
    @discord.option(
        "query", description="Song name, URL, or search query", required=True
    )
    async def play(self, ctx, query: str):
        """Play music in voice channels."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond(
                "❌ Voice features are disabled. Enable LAVALINK_V4_ENABLED and ENABLE_VOICE_FEATURES in dev.env",
                ephemeral=True,
            )
            return

        # Defer the response immediately to prevent timeout
        await ctx.response.defer()

        player = await self.ensure_voice(ctx)
        if not player:
            return

        try:
            # Search using Wavelink v4 – prefer source-specific tracks when possible
            if query.startswith("http://") or query.startswith("https://"):
                search_result = await wavelink.Playable.search(query)
            else:
                # Prefer YouTube results for plain text queries
                try:
                    search_result = await wavelink.YouTubeTrack.search(query)
                except Exception:
                    # Fallback to generic search if YouTubeTrack is unavailable
                    search_result = await wavelink.Playable.search(query)

            if not search_result:
                await ctx.followup.send(
                    "❌ No tracks found for that query!", ephemeral=True
                )
                return

            # Wavelink v4 search behaviour:
            # 1. A single Playable object (Track)
            # 2. A Playlist object which contains a `.tracks` list
            # 3. A raw list of Playable tracks

            tracks: List[wavelink.Playable]

            # Simple fallback approach - try to get tracks directly from result
            try:
                # Try the simple approach first - if it's a list, use it directly
                if isinstance(search_result, list) and all(
                    isinstance(item, wavelink.Playable) for item in search_result
                ):
                    tracks = search_result
                    playlist_name = None
                    logging.info(
                        "Using search result as direct list of Playable objects"
                    )
                else:
                    raise ValueError("Need to use complex parsing")
            except (ValueError, TypeError, AttributeError):
                # Case 2 – playlist detected (imported lazily to avoid type issues)
                if hasattr(search_result, "tracks") and isinstance(
                    search_result.tracks, list
                ):
                    tracks = search_result.tracks  # type: ignore
                    playlist_name = getattr(search_result, "name", "playlist")
                    logging.info("Using playlist.tracks format")
                # Case 3 – raw list returned
                elif isinstance(search_result, list):
                    tracks = search_result
                    playlist_name = None
                    logging.info("Using raw list format")
                # Case 1 – single track
                else:
                    tracks = [search_result]  # type: ignore
                    playlist_name = None
                    logging.info("Using single track format")

            # Flatten any nested lists that may exist (edge-cases from some searches)
            flat_tracks: List[wavelink.Playable] = []
            for item in tracks:
                if isinstance(item, list):
                    flat_tracks.extend(item)  # type: ignore[arg-type]
                else:
                    flat_tracks.append(item)  # type: ignore[arg-type]

            tracks = flat_tracks

            # Guard against empty list (shouldn't happen)
            if not tracks:
                await ctx.followup.send(
                    "❌ No playable tracks found in the search result.",
                    ephemeral=True,
                )
                return

            # Debug logging to understand what we're working with
            logging.info(f"Search result type: {type(search_result)}")
            logging.info(f"Search result: {search_result}")
            logging.info(f"Tracks list type: {type(tracks)}")
            logging.info(f"Tracks list length: {len(tracks)}")
            if tracks:
                logging.info(f"First item in tracks type: {type(tracks[0])}")
                logging.info(f"First item in tracks: {tracks[0]}")

            # Alternative approach: try to get a track directly from search result
            first_track = None

            # Try to find the first valid track in our processed tracks list
            if tracks:
                for item in tracks:
                    if isinstance(item, wavelink.Playable):
                        first_track = item
                        break
                    elif hasattr(item, "__iter__") and not isinstance(item, str):
                        # Handle nested structures
                        for sub_item in item:
                            if isinstance(sub_item, wavelink.Playable):
                                first_track = sub_item
                                break
                        if first_track:
                            break

            # Fallback: try to extract directly from original search result
            if not first_track:
                logging.warning(
                    "Could not find track in processed list, trying direct extraction"
                )
                if isinstance(search_result, wavelink.Playable):
                    first_track = search_result
                elif isinstance(search_result, list) and search_result:
                    for item in search_result:
                        if isinstance(item, wavelink.Playable):
                            first_track = item
                            break
                elif hasattr(search_result, "tracks") and search_result.tracks:
                    for item in search_result.tracks:
                        if isinstance(item, wavelink.Playable):
                            first_track = item
                            break

            if not first_track:
                await ctx.followup.send(
                    "❌ No valid playable tracks found in search results.",
                    ephemeral=True,
                )
                return

            logging.info(f"Selected first track type: {type(first_track)}")
            logging.info(f"Selected first track: {first_track}")

            # Validate that first_track is actually a Playable object
            if not isinstance(first_track, wavelink.Playable):
                await ctx.followup.send(
                    f"❌ Invalid track type received: {type(first_track)}. Expected wavelink.Playable.",
                    ephemeral=True,
                )
                return

            # If something is already playing, queue the new track instead of
            # calling `play()` again. Calling `play()` while the player is
            # active can result in the underlying wavelink implementation
            # receiving a list of tracks and subsequently raising
            # AttributeError: 'list' object has no attribute '_loaded'.

            # Extract all valid tracks for queueing
            valid_tracks = []
            for item in tracks:
                if isinstance(item, wavelink.Playable):
                    valid_tracks.append(item)
                elif hasattr(item, "__iter__") and not isinstance(item, str):
                    for sub_item in item:
                        if isinstance(sub_item, wavelink.Playable):
                            valid_tracks.append(sub_item)

            if player.playing:
                # Add all valid tracks to the custom queue
                for track in valid_tracks:
                    await player.add_track(track)

                added_msg = (
                    f"🎵 **Added** {len(valid_tracks)} tracks from {playlist_name} to the queue"
                    if playlist_name
                    else (
                        f"🎵 **Added to queue:** {first_track.title}"
                        if len(valid_tracks) == 1
                        else f"🎵 **Added** {len(valid_tracks)} tracks to the queue"
                    )
                )

                await ctx.followup.send(added_msg)
            else:
                # Nothing is currently playing – start playback immediately

                # Final safety check: ensure first_track is definitely a single Playable object
                if isinstance(first_track, list):
                    logging.error(
                        f"CRITICAL ERROR: first_track is still a list with {len(first_track)} items: {[type(item) for item in first_track]}"
                    )
                    if first_track and isinstance(first_track[0], wavelink.Playable):
                        logging.info(
                            "Extracting first item from list as emergency fallback"
                        )
                        first_track = first_track[0]
                    else:
                        await ctx.followup.send(
                            "❌ Critical error: Could not extract a valid track from search results.",
                            ephemeral=True,
                        )
                        return
                elif not isinstance(first_track, wavelink.Playable):
                    logging.error(
                        f"CRITICAL ERROR: first_track is not a Playable object: {type(first_track)}"
                    )
                    await ctx.followup.send(
                        f"❌ Critical error: Invalid track type: {type(first_track)}",
                        ephemeral=True,
                    )
                    return

                try:
                    logging.info(
                        f"Attempting to play track: {first_track.title} (type: {type(first_track)})"
                    )
                    logging.info(f"Track attributes: {dir(first_track)}")
                    logging.info(
                        f"Track source: {getattr(first_track, 'source', 'unknown')}"
                    )
                    logging.info(
                        f"Track identifier: {getattr(first_track, 'identifier', 'unknown')}"
                    )

                    # Resolve a clean, single playable via Pool.fetch_tracks using URI/identifier
                    resolved_candidate = None
                    try:
                        candidate_query = None
                        uri = getattr(first_track, "uri", None)
                        identifier = getattr(first_track, "identifier", None)
                        source = getattr(first_track, "source", None)
                        if uri:
                            candidate_query = uri
                        elif identifier and source == "youtube":
                            candidate_query = (
                                f"https://www.youtube.com/watch?v={identifier}"
                            )
                        elif identifier:
                            candidate_query = identifier

                        if candidate_query:
                            fetched = await wavelink.Pool.fetch_tracks(candidate_query)
                            # fetched may be a list or have .tracks
                            fetched_list = (
                                fetched.tracks
                                if hasattr(fetched, "tracks")
                                else fetched
                            )
                            if isinstance(fetched_list, list) and fetched_list:
                                # Prefer an item with a valid encoded payload
                                for t in fetched_list:
                                    try:
                                        enc = getattr(t, "encoded", None)
                                        if enc and not isinstance(enc, list):
                                            resolved_candidate = t
                                            break
                                    except Exception:
                                        continue
                                if not resolved_candidate:
                                    resolved_candidate = fetched_list[0]
                    except Exception as resolve_error:
                        logging.warning(f"Track resolve step failed: {resolve_error}")

                    target_track = resolved_candidate or first_track
                    await player.play(target_track)

                    player.current_track = first_track
                    logging.info("Track started successfully")
                except Exception as play_error:
                    logging.error(f"Error calling player.play(): {play_error}")
                    logging.error(f"first_track type at error: {type(first_track)}")
                    logging.error(f"first_track content at error: {first_track}")

                    # If all else fails, report the error
                    await ctx.followup.send(
                        f"❌ Failed to start playback: {play_error}",
                        ephemeral=True,
                    )
                    return

                # Queue the remaining tracks (if any) into the custom queue
                for track in valid_tracks[1:]:
                    await player.add_track(track)

                now_playing_msg = (
                    f"🎵 **Now playing:** {first_track.title}"
                    if len(valid_tracks) == 1
                    else f"🎵 **Now playing:** {first_track.title} (+{len(valid_tracks) - 1} queued)"
                )

                await ctx.followup.send(now_playing_msg)

        except Exception as e:
            await ctx.followup.send(f"❌ Error playing music: {e}", ephemeral=True)

    @commands.slash_command(
        name="pause",
        description="Pause the current music",
        guild_ids=None,
    )
    async def pause(self, ctx):
        """Pause the current music."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        if player.playing:
            await player.pause()
            await ctx.respond("⏸️ **Paused** the music")
        else:
            await ctx.respond("❌ Nothing is currently playing!", ephemeral=True)

    @commands.slash_command(
        name="resume",
        description="Resume the paused music",
        guild_ids=None,
    )
    async def resume(self, ctx):
        """Resume the paused music."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        if player.is_paused():
            await player.resume()
            await ctx.respond("▶️ **Resumed** the music")
        else:
            await ctx.respond("❌ Music is not paused!", ephemeral=True)

    @commands.slash_command(
        name="stop",
        description="Stop playing and clear the queue",
        guild_ids=None,
    )
    async def stop(self, ctx):
        """Stop playing and clear the queue."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        await player.stop()
        await player.clear_queue()

        await ctx.respond("⏹️ **Stopped** playing and cleared the queue")

    @commands.slash_command(
        name="skip",
        description="Skip the current track",
        guild_ids=None,
    )
    async def skip(self, ctx):
        """Skip the current track."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        if not player.playing:
            await ctx.respond("❌ Nothing is currently playing!", ephemeral=True)
            return

        # Add vote
        player.skip_votes.add(ctx.author.id)

        if len(player.skip_votes) >= player.required_votes:
            await player.stop()
            player.skip_votes.clear()
            await ctx.respond("⏭️ **Skipped** the current track")
        else:
            votes_needed = player.required_votes - len(player.skip_votes)
            await ctx.respond(
                f"🗳️ **Skip vote** added! {votes_needed} more votes needed to skip"
            )

    @commands.slash_command(
        name="queue",
        description="Show the current music queue",
        guild_ids=None,
    )
    async def queue(self, ctx):
        """Show the current music queue."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        queue_info = await player.get_queue_info()
        await ctx.respond(queue_info)

    @commands.slash_command(
        name="volume",
        description="Set the music volume (0-100)",
        guild_ids=None,
    )
    @discord.option(
        "level",
        description="Volume level (0-100)",
        min_value=0,
        max_value=100,
        required=True,
    )
    async def volume(self, ctx, level: int):
        """Set the music volume."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        await player.set_volume(level)
        player.volume = level
        await ctx.respond(f"🔊 **Volume** set to {level}%")

    @commands.slash_command(
        name="nowplaying",
        description="Show information about the currently playing track",
        guild_ids=None,
    )
    async def nowplaying(self, ctx):
        """Show information about the currently playing track."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        player = self.get_player(ctx.guild.id)
        if not player:
            await ctx.respond("❌ No active music player found!", ephemeral=True)
            return

        if not player.playing or not player.current_track:
            await ctx.respond("❌ Nothing is currently playing!", ephemeral=True)
            return

        track = player.current_track
        duration = str(timedelta(seconds=int(track.length)))
        position = str(timedelta(seconds=int(player.position)))

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track.title}**",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Duration", value=f"{position} / {duration}", inline=True)
        embed.add_field(name="Volume", value=f"{player.volume}%", inline=True)
        embed.add_field(
            name="Queue", value=f"{len(player.custom_queue)} tracks", inline=True
        )

        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="disconnect",
        description="Disconnect from the voice channel",
        guild_ids=None,
    )
    async def disconnect(self, ctx):
        """Disconnect from the voice channel."""
        if not self.lavalink_enabled or not self.voice_enabled:
            await ctx.respond("❌ Voice features are disabled.", ephemeral=True)
            return

        if not ctx.voice_client:
            await ctx.respond("❌ I'm not in a voice channel!", ephemeral=True)
            return

        await ctx.voice_client.disconnect()

        # Clean up player
        if ctx.guild.id in self.players:
            del self.players[ctx.guild.id]

        await ctx.respond("👋 **Disconnected** from voice channel")

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: MusicPlayer, track: wavelink.Playable, reason
    ):
        """Handle track end events."""
        logging.info(
            f"Track ended: {track.title if hasattr(track, 'title') else track} - Reason: {reason}"
        )
        logging.info(
            f"Player state - playing: {player.playing}, queue length: {len(player.custom_queue)}"
        )

        try:
            # Loop single track
            if player.loop_mode == "single":
                if isinstance(track, list):
                    logging.error(
                        f"CRITICAL ERROR: track in loop is a list with {len(track)} items: {[type(item) for item in track]}"
                    )
                    track = (
                        track[0]
                        if track and isinstance(track[0], wavelink.Playable)
                        else None
                    )
                if isinstance(track, wavelink.Playable):
                    logging.info(f"Looping single track: {track.title}")
                    await player.play(track)
                else:
                    logging.warning(
                        f"Track end handler received non-Playable track: {type(track)}"
                    )
                return

            # Queue loop: re-add finished track
            if player.loop_mode == "queue" and isinstance(track, wavelink.Playable):
                logging.info(f"Adding track back to queue: {track.title}")
                await player.add_track(track)

            # Play next from queue
            next_track = await player.get_next_track()
            if isinstance(next_track, list):
                logging.error(
                    f"CRITICAL ERROR: next_track is a list with {len(next_track)} items: {[type(item) for item in next_track]}"
                )
                next_track = (
                    next_track[0]
                    if next_track and isinstance(next_track[0], wavelink.Playable)
                    else None
                )

            if isinstance(next_track, wavelink.Playable):
                logging.info(f"Playing next track from queue: {next_track.title}")
                try:
                    await player.play(next_track)
                    logging.info(f"Successfully started playing: {next_track.title}")
                except Exception as play_error:
                    logging.error(f"Failed to play next track: {play_error}")
                    # Try to play the next track in queue
                    next_next_track = await player.get_next_track()
                    if isinstance(next_next_track, wavelink.Playable):
                        try:
                            await player.play(next_next_track)
                            logging.info(
                                f"Successfully started playing fallback track: {next_next_track.title}"
                            )
                        except Exception as fallback_error:
                            logging.error(
                                f"Failed to play fallback track: {fallback_error}"
                            )
            else:
                logging.info("No more tracks in queue, scheduling disconnect")
                # Schedule disconnect after 5 minutes of inactivity
                await asyncio.sleep(300)  # 5 minutes
                if not player.playing and len(player.custom_queue) == 0:
                    try:
                        await player.disconnect()
                        logging.info("Disconnected due to inactivity")
                    except Exception as disconnect_error:
                        logging.error(f"Error disconnecting: {disconnect_error}")

        except Exception as e:
            logging.error(f"Error in track end handler: {e}")
            # Try to recover by playing next track if available
            try:
                next_track = await player.get_next_track()
                if isinstance(next_track, wavelink.Playable):
                    await player.play(next_track)
                    logging.info(f"Recovered and playing: {next_track.title}")
            except Exception as recovery_error:
                logging.error(
                    f"Failed to recover from track end error: {recovery_error}"
                )


def setup(bot):
    bot.add_cog(Music(bot))
