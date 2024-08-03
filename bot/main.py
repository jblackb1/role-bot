import os
import sys
import yaml
import asyncio
import discord
import logging

from keep_alive import keep_alive

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# stdout handler and add it to the logger
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdout_handler)

from role_bot import RoleBot

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Get the base directory and construct the path to the config.yaml file
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'config', 'bingo_config.yaml')

config = load_config(config_path)

API_KEY = config["API_KEY"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

async def load(bot):
    for filename in os.listdir('./bot/cogs'):
        if filename.endswith('cog.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main(bot):
    keep_alive()
    logger.info("RoleBot starting...")
    await load(bot)
    await bot.start(API_KEY)

if __name__ == "__main__":
    bot = RoleBot(intents=intents, command_prefix="!")
    asyncio.run(main(bot))