import logging

import discord
from discord.ext import commands
import logging
import random
import asyncio
import yaml
from os import environ
import motor.motor_asyncio
from core.ai.history import History
import google.generativeai as genai
from google.genai import types
import json


class GamblingGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_bets = {}  # Stores active betting pools
        self.active_trivia = {}  # Stores active trivia games
        self.trivia_questions = self._load_trivia_questions()
        self.emojis = ["🇦", "🇧", "🇨", "🇩"]  # Emojis for multiple choice

        # Initialize database connection for trivia leaderboards
        if hasattr(bot, "DBConn") and bot.DBConn is not None:
            self.DBConn = bot.DBConn
            logging.info("GamblingGames cog using shared database connection")
        else:
            try:
                self.DBConn: History = History(
                    bot=bot,
                    db_conn=motor.motor_asyncio.AsyncIOMotorClient(
                        environ.get("MONGO_DB_URL")
                    ),
                )
                logging.info("GamblingGames cog created fallback database connection")
            except Exception as e:
                logging.error(
                    f"Failed to initialize database connection in GamblingGames cog: {e}"
                )
                self.DBConn = None

        # Pollinations.AI is the primary AI provider
        pass

    def _load_trivia_questions(self):
        try:
            with open("data/trivia_questions.yaml", "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.error("data/trivia_questions.yaml not found.")
            return {}
        except yaml.YAMLError as e:
            logging.error(f"Error parsing trivia_questions.yaml: {e}")
            return {}

    async def _generate_ai_questions(self, topic: str, rounds: int):
        # AI question generation has been removed - using pollinations::evil instead
        # For now, return a message indicating the feature is being updated
        return (
            None,
            "AI question generation is being updated to use Pollinations.AI. Please use static categories for now.",
        )

    @commands.slash_command(name="create_bet", description="Create a new betting pool.")
    @commands.has_permissions(manage_channels=True)
    async def create_bet(
        self,
        ctx: discord.ApplicationContext,
        title: str,
        options: str,
        duration_minutes: int = 5,
    ):
        if ctx.guild.id in self.active_bets:
            await ctx.respond(
                "There's already an active bet in this server. Finish or cancel it first.",
                ephemeral=True,
            )
            return

        bet_options = [opt.strip() for opt in options.split(",")]
        if len(bet_options) < 2:
            await ctx.respond(
                "You need at least two options for a bet.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"💰 New Bet: {title}",
            description="Place your bets by reacting with the corresponding emoji!",
            color=discord.Color.gold(),
        )
        options_text = ""
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        self.active_bets[ctx.guild.id] = {
            "title": title,
            "options": {},
            "participants": {},
            "message_id": None,
            "channel_id": ctx.channel.id,
            "creator_id": ctx.author.id,
            "end_time": asyncio.get_event_loop().time() + duration_minutes * 60,
        }

        for i, option in enumerate(bet_options):
            if i < len(emojis):
                emoji = emojis[i]
                options_text += f"{emoji} {option}\n"
                self.active_bets[ctx.guild.id]["options"][emoji] = {
                    "option_text": option,
                    "votes": 0,
                }
            else:
                await ctx.respond(
                    "Too many options! Maximum 10 options allowed.", ephemeral=True
                )
                del self.active_bets[ctx.guild.id]
                return

        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(
            text=f"Bet ends in {duration_minutes} minutes. Good luck, degens! 💀"
        )

        message = await ctx.respond(embed=embed)
        self.active_bets[ctx.guild.id]["message_id"] = message.id

        for i in range(len(bet_options)):
            if i < len(emojis):
                try:
                    await message.add_reaction(emojis[i])
                except discord.errors.Forbidden:
                    logging.warning(
                        f"Could not add reaction to betting message {message.id} - missing 'Add Reactions' permission"
                    )
                except Exception as e:
                    logging.error(
                        f"Error adding reaction to betting message {message.id}: {e}"
                    )

        self.bot.loop.create_task(
            self._end_bet_timer(ctx.guild.id, duration_minutes * 60)
        )
        logging.info(f"Bet '{title}' created in {ctx.guild.name} by {ctx.author.name}")

    async def _end_bet_timer(self, guild_id: int, delay: int):
        await asyncio.sleep(delay)
        if guild_id in self.active_bets:
            await self._end_bet(guild_id)

    async def _end_bet(self, guild_id: int):
        bet_data = self.active_bets.pop(guild_id)
        channel = self.bot.get_channel(bet_data["channel_id"])
        if not channel:
            logging.error(f"Channel {bet_data['channel_id']} not found for ending bet.")
            return

        message = await channel.fetch_message(bet_data["message_id"])
        if not message:
            logging.error(f"Message {bet_data['message_id']} not found for ending bet.")
            return

        # Recalculate votes from reactions
        for reaction in message.reactions:
            if str(reaction.emoji) in bet_data["options"]:
                bet_data["options"][str(reaction.emoji)]["votes"] = (
                    reaction.count - 1
                )  # Subtract bot's own reaction

        results_text = "### Bet Results:\n"
        total_votes = 0
        for emoji, option_info in bet_data["options"].items():
            results_text += (
                f"{emoji} {option_info['option_text']}: {option_info['votes']} votes\n"
            )
            total_votes += option_info["votes"]

        if total_votes == 0:
            results_text += "\nNo one dared to bet? Y'all broke or what? 💀"
        else:
            # Determine winner (most votes)
            winning_option = None
            max_votes = -1
            for emoji, option_info in bet_data["options"].items():
                if option_info["votes"] > max_votes:
                    max_votes = option_info["votes"]
                    winning_option = option_info["option_text"]
                elif option_info["votes"] == max_votes and winning_option:
                    winning_option += (
                        f" and {option_info['option_text']}"  # Handle ties
                    )

            results_text += f"\n### Winner: {winning_option}! EZ money for some, ramen for the rest. 💰"

        embed = discord.Embed(
            title=f"💸 Bet Ended: {bet_data['title']}",
            description=results_text,
            color=discord.Color.dark_gold(),
        )
        await channel.send(embed=embed)
        logging.info(f"Bet '{bet_data['title']}' ended in {channel.guild.name}")

    @commands.slash_command(
        name="cancel_bet", description="Cancel the current active betting pool."
    )
    @commands.has_permissions(manage_channels=True)
    async def cancel_bet(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_bets:
            bet_data = self.active_bets.pop(ctx.guild.id)
            await ctx.respond(
                f"Bet '{bet_data['title']}' has been cancelled. Jakey don't refund, but y'all got lucky this time. 💀",
                ephemeral=False,
            )
            logging.info(f"Bet '{bet_data['title']}' cancelled in {ctx.guild.name}")
        else:
            await ctx.respond("No active bet to cancel in this server.", ephemeral=True)

    @commands.slash_command(name="trivia", description="Start a trivia game.")
    @discord.option(
        "category",
        description="Choose a category or type a topic for AI-generated questions.",
        required=False,
    )
    @discord.option(
        "rounds",
        description="Number of questions to play (default: 5).",
        min_value=1,
        max_value=10,
        default=5,
        required=False,
    )
    async def trivia(
        self, ctx: discord.ApplicationContext, category: str = None, rounds: int = 5
    ):
        if ctx.guild.id in self.active_trivia:
            await ctx.respond(
                "There's already a trivia game active in this server. Finish or cancel it first.",
                ephemeral=True,
            )
            return

        await ctx.defer()

        questions_to_play = []
        if category and category in self.trivia_questions:
            questions_to_play = random.sample(
                self.trivia_questions[category],
                min(rounds, len(self.trivia_questions[category])),
            )
            logging.info(
                f"Starting static trivia in {ctx.guild.name} for category '{category}' with {len(questions_to_play)} rounds."
            )
        elif category:
            # AI-generated questions
            ai_questions, error_message = await self._generate_ai_questions(
                category, rounds
            )
            if error_message:
                await ctx.followup.send(error_message)
                return
            questions_to_play = ai_questions
            logging.info(
                f"Starting AI-generated trivia in {ctx.guild.name} for topic '{category}' with {len(questions_to_play)} rounds."
            )
        else:
            # Default to a random static category if no category is provided
            if not self.trivia_questions:
                await ctx.followup.send(
                    "Jakey ain't got no trivia questions loaded. Tell the admin to add some or try an AI topic! 💀"
                )
                return
            random_category_name = random.choice(list(self.trivia_questions.keys()))
            questions_to_play = random.sample(
                self.trivia_questions[random_category_name],
                min(rounds, len(self.trivia_questions[random_category_name])),
            )
            logging.info(
                f"Starting random static trivia in {ctx.guild.name} for category '{random_category_name}' with {len(questions_to_play)} rounds."
            )

        if not questions_to_play:
            await ctx.followup.send(
                "Couldn't find or generate any trivia questions for that. Try a different category or topic. Rigged. 💀"
            )
            return

        self.active_trivia[ctx.guild.id] = {
            "questions": questions_to_play,
            "current_round": 0,
            "scores": {},  # {user_id: score}
            "channel_id": ctx.channel.id,
            "message_id": None,
            "timer_task": None,
            "correct_answer_user": None,
            "category": category if category else "Random Static",
        }

        await ctx.followup.send(
            f"🧠 Trivia game starting in {self.active_trivia[ctx.guild.id]['category']} category with {len(questions_to_play)} rounds! Get ready, degens! 🔥"
        )
        self.bot.loop.create_task(self._run_trivia_game(ctx.guild.id))

    async def _run_trivia_game(self, guild_id: int):
        trivia_data = self.active_trivia[guild_id]
        channel = self.bot.get_channel(trivia_data["channel_id"])
        if not channel:
            logging.error(
                f"Channel {trivia_data['channel_id']} not found for trivia game."
            )
            self.active_trivia.pop(guild_id, None)
            return

        for i in range(len(trivia_data["questions"])):
            trivia_data["current_round"] = i
            question_data = trivia_data["questions"][i]
            trivia_data["correct_answer_user"] = None  # Reset for new round

            options_text = "\n".join(
                [
                    f"{self.emojis[j]} {opt}"
                    for j, opt in enumerate(question_data["options"])
                ]
            )

            embed = discord.Embed(
                title=f"🧠 Round {i + 1}/{len(trivia_data['questions'])}: Trivia Time! 🧠",
                description=f"**Question:** {question_data['question']}\n\n{options_text}\n\nYou have 20 seconds! React with your answer! ⏰",
                color=discord.Color.blue(),
            )
            message = await channel.send(embed=embed)
            trivia_data["message_id"] = message.id

            for emoji in self.emojis[: len(question_data["options"])]:
                try:
                    await message.add_reaction(emoji)
                except discord.errors.Forbidden:
                    logging.warning(
                        f"Could not add reaction to trivia message {message.id} - missing 'Add Reactions' permission"
                    )
                except Exception as e:
                    logging.error(
                        f"Error adding reaction to trivia message {message.id}: {e}"
                    )

            # Start timer for this round
            trivia_data["timer_task"] = self.bot.loop.create_task(
                self._end_trivia_round_timer(guild_id, 20)
            )

            try:
                await asyncio.wait_for(
                    self._wait_for_correct_answer(guild_id), timeout=20
                )
            except asyncio.TimeoutError:
                await channel.send(
                    f"⏰ Time's up for Round {i + 1}! No one got it this time. The answer was **{question_data['answer']}**."
                )

            if trivia_data["timer_task"] and not trivia_data["timer_task"].done():
                trivia_data["timer_task"].cancel()

            await asyncio.sleep(5)  # Pause between rounds

        # End of game
        await self._end_trivia_game(guild_id)

    async def _wait_for_correct_answer(self, guild_id: int):
        # This function will be awaited until a correct answer is registered
        # The _end_trivia_round_timer will handle the timeout
        while (
            self.active_trivia.get(guild_id)
            and self.active_trivia[guild_id]["correct_answer_user"] is None
        ):
            await asyncio.sleep(1)  # Check every second

    async def _end_trivia_round_timer(self, guild_id: int, delay: int):
        await asyncio.sleep(delay)
        if guild_id in self.active_trivia:
            # If no one got it right, the _run_trivia_game loop will handle the message
            pass  # The main loop will proceed to the next round or end the game

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot or not reaction.message.guild:
            return

        guild_id = reaction.message.guild.id
        if (
            guild_id in self.active_trivia
            and reaction.message.id == self.active_trivia[guild_id]["message_id"]
        ):
            trivia_data = self.active_trivia[guild_id]
            current_question = trivia_data["questions"][trivia_data["current_round"]]

            if trivia_data["correct_answer_user"] is not None:  # Already answered
                return

            try:
                chosen_option_index = self.emojis.index(str(reaction.emoji))
                if chosen_option_index < len(current_question["options"]):
                    # Compare chosen emoji with the emoji corresponding to the correct answer letter
                    if (
                        str(reaction.emoji)
                        == self.emojis[
                            ord(current_question["answer"].upper()) - ord("A")
                        ]
                    ):
                        # Correct answer!
                        if (
                            trivia_data["timer_task"]
                            and not trivia_data["timer_task"].done()
                        ):
                            trivia_data["timer_task"].cancel()  # Stop the timer

                        time_taken = (
                            asyncio.get_event_loop().time()
                            - reaction.message.created_at.timestamp()
                        )
                        score_awarded = max(
                            1, 20 - int(time_taken)
                        )  # Faster answers get more points

                        trivia_data["scores"][user.id] = (
                            trivia_data["scores"].get(user.id, 0) + score_awarded
                        )
                        trivia_data["correct_answer_user"] = user.id  # Mark as answered

                        await reaction.message.channel.send(
                            f"💰 {user.mention} got it! The answer was '{current_question['options'][chosen_option_index]}'. Awarded {score_awarded} points!"
                        )
                        logging.info(
                            f"User {user.name} answered correctly in trivia round {trivia_data['current_round'] + 1}."
                        )
                    else:
                        # Incorrect answer - Jakey can roast
                        roasts = [
                            f"Nah, {user.mention}, that ain't it. You're as off as my last parlay. 💀",
                            f"Wrong answer, {user.mention}. Did you even try? Rigged. 🔥",
                            f"Close, but no cigar, {user.mention}. Keep gambling those guesses. 🎰",
                        ]
                        if random.random() < 0.3:  # 30% chance to roast
                            await reaction.message.channel.send(random.choice(roasts))
            except ValueError:
                pass  # Not a trivia emoji

    async def _end_trivia_game(self, guild_id: int):
        trivia_data = self.active_trivia.pop(guild_id, None)
        if not trivia_data:
            return

        channel = self.bot.get_channel(trivia_data["channel_id"])
        if not channel:
            logging.error(
                f"Channel {trivia_data['channel_id']} not found for ending trivia game."
            )
            return

        results_text = "### Final Trivia Results:\n"
        if not trivia_data["scores"]:
            results_text += "No one scored any points. Y'all need to hit the books, not the slots. 💀"
        else:
            sorted_scores = sorted(
                trivia_data["scores"].items(), key=lambda item: item[1], reverse=True
            )
            for user_id, score in sorted_scores:
                user = self.bot.get_user(user_id)
                results_text += f"• {user.mention}: {score} points\n"

            top_player_id = sorted_scores[0][0]
            top_player = self.bot.get_user(top_player_id)
            results_text += f"\n### Winner: {top_player.mention}! 🏆\n"
            results_text += "EZ money for them, better luck next time, degens! 💰"

            # Save scores to database
            if self.DBConn:
                for user_id, score in trivia_data["scores"].items():
                    await self.DBConn.add_trivia_score(guild_id, user_id, score)

        embed = discord.Embed(
            title="🧠 Trivia Game Ended! 🧠",
            description=results_text,
            color=discord.Color.dark_blue(),
        )
        await channel.send(embed=embed)
        logging.info(f"Trivia game ended in {channel.guild.name}")

    @commands.slash_command(
        name="cancel_trivia", description="Cancel the current active trivia game."
    )
    @commands.has_permissions(manage_channels=True)
    async def cancel_trivia(self, ctx: discord.ApplicationContext):
        if ctx.guild.id in self.active_trivia:
            trivia_data = self.active_trivia.pop(ctx.guild.id)
            if trivia_data["timer_task"] and not trivia_data["timer_task"].done():
                trivia_data["timer_task"].cancel()
            await ctx.respond(
                f"Trivia game has been cancelled. Jakey's bored anyway. 💀",
                ephemeral=False,
            )
            logging.info(f"Trivia cancelled in {ctx.guild.name}")
        else:
            await ctx.respond(
                "No active trivia game to cancel in this server.", ephemeral=True
            )

    @commands.slash_command(
        name="trivia_leaderboard", description="Show the all-time trivia leaderboard."
    )
    async def trivia_leaderboard(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        if not self.DBConn:
            await ctx.followup.send(
                "❌ Database connection not available for leaderboards."
            )
            return

        guild_id = ctx.guild.id if ctx.guild else ctx.author.id
        leaderboard_data = await self.DBConn.get_trivia_leaderboard(guild_id, limit=10)

        if not leaderboard_data:
            await ctx.followup.send(
                "No one's on the leaderboard yet. Get gambling on some trivia! 🎰"
            )
            return

        leaderboard_text = ""
        for i, entry in enumerate(leaderboard_data):
            user = self.bot.get_user(entry["user_id"])
            if user:
                leaderboard_text += (
                    f"{i + 1}. {user.mention}: {entry['score']} points\n"
                )
            else:
                leaderboard_text += f"{i + 1}. Unknown User ({entry['user_id']}): {entry['score']} points\n"

        embed = discord.Embed(
            title="🏆 All-Time Trivia Leaderboard 🏆",
            description=leaderboard_text,
            color=discord.Color.purple(),
        )
        await ctx.followup.send(embed=embed)
        logging.info(f"Trivia leaderboard displayed for {ctx.guild.name}")


def setup(bot):
    bot.add_cog(GamblingGames(bot))
