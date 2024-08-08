import logging
import discord
from discord.ext import commands
from discord import app_commands 



logger = logging.getLogger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{self.bot.user.name}  Admin cog has started. Guild ID for validation: {self.bot.guild_id}')
        await self.sync_commands()

    @commands.command(name="resync")
    async def resync(self, ctx):
        logging.info(f'Command Tree before clearing: {self.bot.tree}')
        if self.bot.tree:
            #guild = discord.Object(id=self.bot.guild_id)
            await self.bot.tree.clear_commands(guild=None)
            await self.sync_commands()
            await ctx.send(f'Synced slash commands.')
        else:
            logger.warning('Bot command tree does not exist')

    async def sync_commands(self):
        if self.bot.guild_id:
            guild = discord.Object(id=self.bot.guild_id)
            result = await self.bot.tree.sync(guild=guild)
            logging.info(f'Synced {len(result)} slash commands synced to guild {self.bot.guild_id}.')
        else:
            result = await self.bot.tree.sync()
            logging.info(f'Synced {len(result)} slash commands synced globally.')

async def setup(bot):
    await bot.add_cog(AdminCog(bot))