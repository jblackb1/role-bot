import os
import asyncio
import discord
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
    await load(bot)
    await bot.start(APIKEY)

if __name__ == "__main__":
    bot = RoleBot(intents=intents, command_prefix="!")
    asyncio.run(main(bot))