import re
import random
import logging
import discord
from discord.ext import commands
from discord import app_commands 



logger = logging.getLogger(__name__)

dice_pattern = re.compile(r'(\d*)d(\d+)([+-]\d+)?')

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{self.bot.user.name}  Dice Roller cog has started.')

    @app_commands.command(name="roll",
                          description="Roll dice based on the given expression")
    @app_commands.describe(expression="The dice expression to roll. Format: <num of dice>d<die size>+<modifier> e.x. 2d6+4")
    async def roll(self, interaction: discord.Interaction, expression: str):
        try:
            total, breakdown = self.roll_dice(expression)
            await interaction.response.send_message(f'{expression} = {total} ({breakdown})')
        except Exception as e:
            await interaction.response.send_message(f'Error: {str(e)}')

    def roll_dice(self, expression: str):
        matches = dice_pattern.findall(expression)
        if not matches:
            raise ValueError("Invalid dice expression")
        
        total = 0
        breakdown = []
        for match in matches:
            num_dice = int(match[0]) if match[0] else 1
            die_sides = int(match[1])
            modifier = int(match[2]) if match[2] else 0

            rolls = [random.randint(1, die_sides) for _ in range(num_dice)]
            subtotal = sum(rolls) + modifier

            breakdown.append(f"({' + '.join(map(str, rolls))}){' + ' if modifier > 0 else ''}{modifier if modifier != 0 else ''}")
            total += subtotal

            return total, ' + '.join(breakdown)


async def setup(bot):
    await bot.add_cog(DiceCog(bot))