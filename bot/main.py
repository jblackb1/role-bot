import os
import asyncio
import discord
import logging
import sys

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# stdout handler and add it to the logger
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdout_handler)

from role_bot import RoleBot
from config.bingo_config import APIKEY

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

async def load(bot):
    for filename in os.listdir('./bot/cogs'):
        if filename.endswith('cog.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main(bot):
    logger.info("RoleBot starting...")
    await load(bot)
    await bot.start(APIKEY)

if __name__ == "__main__":
    bot = RoleBot(intents=intents, command_prefix="!")
    asyncio.run(main(bot))