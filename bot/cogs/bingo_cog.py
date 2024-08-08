import os
import yaml
import logging
import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger(__name__)

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Get the base directory and construct the path to the config.yaml file
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '..', 'config', 'bingo_config.yaml')

config = load_config(config_path)

# Now you can access the config values like this:
dungeon_master = config['DUNGEON_MASTER']
command_channel_id = config['COMMAND_CHANNEL_ID']
board_channel_id = config['BOARD_CHANNEL_ID']
game_channel_id = config['GAME_CHANNEL_ID']
bingo_size = config['BINGO_SIZE']


class BingoCog(commands.Cog):
    def __init__(self, bot, command_channel_id, game_channel_id, board_channel_id, dungeon_master, bingo_size):
        self.bot = bot
        self.bingo_size = bingo_size
        self.dungeon_master = dungeon_master
        self.game_channel_id = game_channel_id
        self.board_channel_id = board_channel_id
        self.command_channel_id = command_channel_id

    def load_bingo_squares(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bingo_squares_file = os.path.join(base_dir, '..', 'config', 'bingo_squares.yaml')

        with open(bingo_squares_file, 'r') as file:
            bingo_squares = yaml.safe_load(file)

        return bingo_squares

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            logger.info(f'{self.bot.user.name} has connected to Discord!')
            self.game_channel = self.bot.get_channel(self.game_channel_id)
            self.board_channel = self.bot.get_channel(self.board_channel_id)
            self.command_channel = self.bot.get_channel(self.command_channel_id)
            await self.send_commands_message(self.command_channel)
        except Exception as error:
            logger.error(error)

    @commands.command()
    async def select(self, ctx, initials: str = None, row: int = None, col: int = None):
        try:
            selection = {}

            # Only accept selections from the game channel and during the pre-game stage
            if ctx.channel.id != self.game_channel.id:
                if self.bot.game_save.game_state != 0:
                    await ctx.send("Game has already started. Please reset your game to add new selections.")
                return

            # Validate the command format and send a format message if incorrect
            if initials is None or row is None or col is None:
                await ctx.send("Invalid command format. Please use: `!select <initials> <row> <column>`")
                return

            if len(initials) != 2:
                await ctx.send(f'<@{ctx.author.id}>: Initials must be exactly 2 characters.')
                return
            
            if row > bingo_size or col > bingo_size:
                await ctx.send(f'Your row or column selection exceeds the size of the board. Enter numbers below {bingo_size}')
                return
            
            # Check if the row and column have already been selected
            existing_selections = self.bot.game_save.selections
            for user_id, existing_selection in existing_selections.items():
                if existing_selection['row'] == row - 1 or existing_selection['col'] == col - 1:
                    await ctx.send(f'<@{ctx.author.id}>: This row or column has already been selected by another player.')
                    return

            member = ctx.guild.get_member(ctx.author.id)
            if member is not None:
                selection[member.id] = {'initials': initials.upper(), 'row': row - 1, 'col': col - 1}
                self.bot.game_save.save_attr(selection)
                await ctx.send(f'<@{ctx.author.id}> has registered with initials {initials.upper()} and selected row {row} and column {col}')

            board = self.bot.bingo_helper.get_current_board()
            if board is None:
                return

            # Refresh the board to display new selections
            board_str = await self.bot.bingo_helper.get_board_display(self.game_channel, self.bot.game_save.current_board)
            await ctx.send(board_str)

            logger.info(f'{member.display_name} has registered with initials {initials.upper()} and selected row {row} and column {col}')

        except Exception as error:
            logger.error(error)

    @app_commands.command(name="setup_game", description="Setup a new bingo game")
    async def setup_game(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            # generate and send jpg of bingo square contents to DM channel
            board_contents = self.bot.bingo_helper.generate_bingo_board(self.load_bingo_squares())
            imagepath = self.bot.bingo_helper.save_board_as_jpg(board_contents)
            with open(imagepath, 'rb') as f:
                picture = discord.File(f)
                await interaction.followup.send("Board contents:", file=picture, ephemeral=True)

            # generate and send blank emoji board to bingo game channel
            board = [[':white_large_square:' for _ in range(self.bingo_size)] for _ in range(self.bingo_size)]
            board_str = await self.bot.bingo_helper.get_board_display(interaction, board)
            await interaction.channel.send(board_str)
            self.bot.game_save.save_attr(current_board=board)

            logger.info('Setting up new Bingo game.')

        except Exception as error:
            logger.error(error, exc_info=True)

    @app_commands.command(name="start_game", description="Start the bingo game. No more selections can be made.")
    async def start_game(self, interaction: discord.Interaction):
        try:
            # Verify command is only coming from DM and command channel
            #if interaction.author.id != self.dungeon_master or interaction.channel.id != self.command_channel.id:
                #return

            # Start the game only if it's in pre-game state
            if self.bot.game_save.game_state == 0:
                self.bot.game_save.save_attr(game_state=1)
                await interaction.channel.send("The game has started. No more selections can be made.")
                board_str = await self.bot.bingo_helper.get_board_display(interaction.channel, self.bot.game_save.current_board)
                await interaction.channel.send(board_str)
                logger.info('Starting the Bingo game now')
            else:
                await interaction.response.send_message("The game has already started. Use !reset_game to start a new game.", ephemeral=True)
                logger.info('User attempted to start the game while it was already started. Doing nothing.')

        except Exception as error:
            logger.error(error)


    @commands.command()
    async def add_square(self, ctx, row: int, col: int):
        try:
            # verify command is only coming from DM and command channel
            if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
                return

            logger.info(f'Row {row} and column {col} being added to the board.')

            # get current bingo board
            board = self.bot.bingo_helper.get_current_board()
            if board is None:
                return

            # set added square to black square emoji to indicate a selection
            board[row - 1][col - 1] = ':black_large_square:'

            winning_user_ids = self.bot.bingo_helper.check_winners(board, self.bingo_size)
            for id in winning_user_ids:
                if id is not None:
                    winning_user = ctx.guild.get_member(id)
                    await self.game_channel.send(f'{winning_user.mention} has won!')
                    logger.info(f'{winning_user.display_name} has won!')

            board_str = await self.bot.bingo_helper.get_board_display(self.game_channel, board)
            await self.game_channel.send(board_str)

            self.bot.game_save.save_attr(current_board=board)

        except Exception as error:
            logger.error(error)

    @commands.command()
    async def remove_square(self, ctx, row: int, col: int):
        try:
            # verify command is only coming from DM and command channel
            if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
                return

            logger.info(f'Row {row} and column {col} being removed from the board.')

            board = await self.get_current_board()
            if board is None:
                return

            # set specified square back to white, save, and send
            board[row - 1][col - 1] = ':white_large_square:'
            board_str = await self.bot.bingo_helper.get_board_display(ctx, board)
            await self.game_channel.send(board_str)

            self.bot.game_save.save_attr(current_board=board)
        except Exception as error:
            logger.error(error)

    @app_commands.command(name="reset_game", description="Reset the game.")
    async def reset_game(self, interaction: discord.Interaction):
        try:
            # verify command is only coming from DM and command channel
            #if interaction.user.id != self.dungeon_master or interaction.channel.id != self.command_channel.id:
            #    return

            logger.info('Resetting the gamesave and removing board and selection messages from the game channel.')

            async for message in interaction.channel.history(limit=100):
                if message.author == self.bot.user and ('Bingo Board' in message.content or 'registered' in message.content):
                    await message.delete()

            # Clear user selections and winners
            self.bot.game_save.reset()

            await interaction.response.send_message("The bingo board and user selections have been reset. You can start a new game using !setup_game.", ephemeral=True)
        except Exception as error:
            logger.error(error)

async def setup(bot):
    await bot.add_cog(BingoCog(bot, command_channel_id, game_channel_id, board_channel_id, dungeon_master, bingo_size))
