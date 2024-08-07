from discord.ext import commands
from bingo.bingo_save import GameSave
from bingo.bingo_helper import BingoHelper


class RoleBot(commands.Bot):
    def __init__(self, intents, command_prefix):
        super().__init__(intents=intents, command_prefix=command_prefix)

        self.bingo_helper = BingoHelper(self)
        self.game_save = GameSave()

    async def on_ready(self):
        await self.tree.sync()