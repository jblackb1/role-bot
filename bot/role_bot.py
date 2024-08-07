import os
import logging
import discord
from discord.ext import commands
from bingo.bingo_save import GameSave
from bingo.bingo_helper import BingoHelper


logger = logging.getLogger(__name__)

class RoleBot(commands.Bot):
    def __init__(self, intents, command_prefix, guild_id=None):
        super().__init__(intents=intents, command_prefix=command_prefix)

        self.guild_id = guild_id
        self.game_save = GameSave()
        self.bingo_helper = BingoHelper(self)

    async def setup_hook(self):
        await self.load_cogs()
        await self.sync_commands()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name}')

    async def load_cogs(self):
        for filename in os.listdir('./bot/cogs'):
            if filename.endswith('cog.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    logger.warning(f'{filename[:-3]} cog not started: {e}')
    
    async def sync_commands(self):
        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            await self.tree.sync(guild=guild)
            logging.info(f'Slash commands synced to guild {self.guild_id}.')
        else:
            await self.tree.sync()
            logging.info('Slash commands synced globally.')