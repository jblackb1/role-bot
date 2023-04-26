from discord.ext import commands
from bingo_save import GameSave
from bingo_helper import BingoHelper
from cogs.bingo_cog import BingoCog


class RoleBot(commands.Bot):
    def __init__(self, intents, command_prefix):
        super().__init__(intents=intents, command_prefix=command_prefix)

        self.bingo_helper = BingoHelper(self)
        self.game_save = GameSave()