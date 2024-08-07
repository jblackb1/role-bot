import os
import sys
import yaml
import asyncio
import discord
import logging

from role_bot import RoleBot
from keep_alive import keep_alive

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# stdout handler and add it to the logger
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdout_handler)

# Get the base directory and construct the path to the config.yaml file
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'config', 'bingo_config.yaml')

# Set intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config(config_path)

API_KEY = config["API_KEY"]
GUILD_ID = config["GUILD_ID"]

# Initialize the bot object
bot = RoleBot(intents=intents, command_prefix="!", guild_id=GUILD_ID)

async def main(bot):
    keep_alive()
    logger.info("RoleBot starting...")
    await bot.start(API_KEY)

if __name__ == "__main__":
    asyncio.run(main(bot))