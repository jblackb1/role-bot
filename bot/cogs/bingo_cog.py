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

bingo_size = config['BINGO_SIZE']


class BingoCog(commands.Cog):
    def __init__(self, bot, bingo_size):
        self.bot = bot
        self.bingo_size = bingo_size

    def load_bingo_squares(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bingo_squares_file = os.path.join(base_dir, '..', 'config', 'bingo_squares.yaml')

        with open(bingo_squares_file, 'r') as file:
            bingo_squares = yaml.safe_load(file)

        return bingo_squares

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{self.bot.user.name} has connected to Discord!')

    @app_commands.command(name="select", description="select a row and column to play bingo with")
    async def select(self, interaction: discord.Interaction, initials: str, row: int, col: int):
        try:
            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)

            selection = {}

            # Only accept selections from the game channel and during the pre-game stage
            if game_save.game_state != 0:
                await interaction.response.send_message("Game has already started. Please reset your game to add new selections.", ephemeral=True)
                return

            if len(initials) != 2:
                await interaction.response.send_message(f'<@{interaction.user.id}>: Initials must be exactly 2 characters.', ephemeral=True)
                return
            
            if row > bingo_size or col > bingo_size:
                await interaction.response.send_message(f'Your row or column selection exceeds the size of the board. Enter numbers below {bingo_size}', ephemeral=True)
                return
            
            # Check if the row and column have already been selected
            existing_selections = game_save.selections
            for user_id, existing_selection in existing_selections.items():
                if existing_selection['row'] == row - 1 or existing_selection['col'] == col - 1:
                    await interaction.response.send_message(f'<@{interaction.user.id}>: This row or column has already been selected by another player.', ephemeral=True)
                    return

            member = interaction.guild.get_member(interaction.user.id)
            if member is not None:
                selection[member.id] = {'initials': initials.upper(), 'row': row - 1, 'col': col - 1}
                game_save.save_attr(selection)
                await interaction.channel.send(f'<@{interaction.user.id}> has registered with initials {initials.upper()} and selected row {row} and column {col}')

            board = self.bot.bingo_helper.get_current_board()
            if board is None:
                return

            # Refresh the board to display new selections
            board_str = await self.bot.bingo_helper.get_board_display(interaction, self.bot.game_save.current_board)
            await interaction.channel.send(board_str)

            logger.info(f'{member.display_name} has registered with initials {initials.upper()} and selected row {row} and column {col}')

        except Exception as error:
            logger.error(error)

    @app_commands.command(name="setup_game", description="Setup a new bingo game")
    async def setup_game(self, interaction: discord.Interaction):
        try:
            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)

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
            game_save.save_attr(current_board=board)

            logger.info('Setting up new Bingo game.')

        except Exception as error:
            logger.error(error, exc_info=True)

    @app_commands.command(name="start_game", description="Start the bingo game. No more selections can be made.")
    async def start_game(self, interaction: discord.Interaction):
        try:
            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)
            # Start the game only if it's in pre-game state
            if game_save.game_state == 0:
                game_save.save_attr(game_state=1)
                await interaction.channel.send("The game has started. No more selections can be made.")
                board_str = await self.bot.bingo_helper.get_board_display(interaction, game_save.current_board)
                await interaction.channel.send(board_str)
                logger.info('Starting the Bingo game now')
            else:
                await interaction.response.send_message("The game has already started. Use !reset_game to start a new game.", ephemeral=True)
                logger.info('User attempted to start the game while it was already started. Doing nothing.')

        except Exception as error:
            logger.error(error)


    @app_commands.command(name="add_square", description="add a filled square to the game board")
    async def add_square(self, interaction: discord.Interaction, row: int, col: int):
        try:
            logger.info(f'Row {row} and column {col} being added to the board.')

            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)

            # get current bingo board
            board = self.bot.bingo_helper.get_current_board()
            if board is None:
                return

            # set added square to black square emoji to indicate a selection
            board[row - 1][col - 1] = ':black_large_square:'

            winning_user_ids = self.bot.bingo_helper.check_winners(board, self.bingo_size, guild_id)
            for id in winning_user_ids:
                if id is not None:
                    winning_user = interaction.guild.get_member(id)
                    await interaction.channel.send(f'{winning_user.mention} has won!')
                    logger.info(f'{winning_user.display_name} has won!')

            board_str = await self.bot.bingo_helper.get_board_display(interaction, board)
            await interaction.channel.send(board_str)

            game_save.save_attr(current_board=board)

        except Exception as error:
            logger.error(error)

    @app_commands.command(name="remove_square", description="remove a specific square from the game board")
    async def remove_square(self, interaction: discord.Interaction, row: int, col: int):
        try:
            logger.info(f'Row {row} and column {col} being removed from the board.')

            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)

            board = await self.bot.bingo_helper.get_current_board()
            if board is None:
                return

            # set specified square back to white, save, and send
            board[row - 1][col - 1] = ':white_large_square:'
            board_str = await self.bot.bingo_helper.get_board_display(interaction, board)
            await interaction.channel.send(board_str)

            game_save.save_attr(current_board=board)
        except Exception as error:
            logger.error(error)

    @app_commands.command(name="reset_game", description="Reset the game.")
    async def reset_game(self, interaction: discord.Interaction):
        try:
            logger.info('Resetting the gamesave and removing board and selection messages from the game channel.')

            guild_id = str(interaction.guild.id)
            game_save = self.bot.get_game_save(guild_id)

            async for message in interaction.channel.history(limit=100):
                if message.author == self.bot.user and ('Bingo Board' in message.content or 'registered' in message.content):
                    await message.delete()

            # Clear user selections and winners
            game_save.reset()

            await interaction.response.send_message("The bingo board and user selections have been reset. You can start a new game using !setup_game.", ephemeral=True)
        except Exception as error:
            logger.error(error)

async def setup(bot):
    await bot.add_cog(BingoCog(bot, bingo_size))
