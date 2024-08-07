import logging
import discord
from discord.ext import commands
from discord import app_commands 



logger = logging.getLogger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sync_commands()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{self.bot.user.name}  Admin cog has started.')

    @commands.command(name="resync")
    async def resync(self, ctx):
        guild = discord.Object(id=self.guild_id)
        await self.tree.clear_commands(guild=guild)
        await self.sync_commands()
        await ctx.send(f'Synced slash commands.')
    
    async def sync_commands(self):
        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            result = await self.tree.sync(guild=guild)
            logging.info(f'Synced {len(result)} slash commands synced to guild {self.guild_id}.')
        else:
            result = await self.tree.sync()
            logging.info(f'Synced {len(result)} slash commands synced globally.')

async def setup(bot):
    await bot.add_cog(AdminCog(bot))