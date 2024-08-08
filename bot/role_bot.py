import os
import logging
import discord
from discord.ext import commands
from bingo.bingo_save import GameSave
from bingo.bingo_helper import BingoHelper


logger = logging.getLogger(__name__)

class RoleBot(commands.Bot):
    def __init__(self, intents, command_prefix):
        super().__init__(intents=intents, command_prefix=command_prefix)
        self.game_saves = {}
        self.bingo_helper = BingoHelper(self)
        logger.info(f'{self.tree}')

    async def setup_hook(self):
        await self.load_cogs()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name}')

    def get_game_save(self, guild_id):
        if guild_id not in self.game_saves:
            self.game_saves[guild_id] = GameSave(guild_id)
        return self.game_saves[guild_id]

    async def load_cogs(self):
        for filename in os.listdir('./bot/cogs'):
            if filename.endswith('cog.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    logger.warning(f'{filename[:-3]} cog not started: {e}')