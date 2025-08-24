from discord.ext import commands
import logging

import discord
import random

class Keno(commands.Cog):
    """Keno number generator commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="keno", description="Generate random Keno numbers (3-10 numbers from 1-40)"
    )
    async def keno(self, ctx):
        """Generate Keno numbers by randomly selecting 3-10 numbers from 1-40"""
        await ctx.response.defer()

        # Generate a random count between 3 and 10
        count = random.randint(3, 10)

        # Generate random numbers from 1-40 without duplicates
        numbers = random.sample(range(1, 41), count)

        # Sort the numbers for better readability
        numbers.sort()

        # Create embed for better presentation
        embed = discord.Embed(
            title="🎯 Keno Number Generator",
            description=f"Generated **{count}** numbers for you!",
            color=discord.Color.green(),
        )

        # Add the numbers as a field
        embed.add_field(
            name="Your Keno Numbers",
            value=f"`{', '.join(map(str, numbers))}`",
            inline=False,
        )

        # Create visual representation
        visual_lines = []
        for row in range(0, 40, 10):
            line = ""
            for i in range(row + 1, min(row + 11, 41)):
                if i in numbers:
                    line += f"[{i:2d}] "
                else:
                    line += f" {i:2d} "
            visual_lines.append(line.strip())

        embed.add_field(
            name="Visual Board",
            value="```\n" + "\n".join(visual_lines) + "\n```",
            inline=False,
        )

        embed.set_footer(text="Numbers in brackets are your picks!")

        await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(Keno(bot))
