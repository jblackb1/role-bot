import discord
from discord.ext import commands
from ..bingo.bingo_squares import bingo_squares
from ..config.bingo_config import COMMAND_CHANNEL_ID, GAME_CHANNEL_ID, BOARD_CHANNEL_ID, DUNGEON_MASTER, BINGO_SIZE


class BingoCog(commands.Cog):
    def __init__(self, bot, command_channel_id, game_channel_id, board_channel_id, dungeon_master, bingo_size, bingo_squares):
        self.bot = bot
        self.bingo_size = bingo_size
        self.bingo_squares = bingo_squares
        self.dungeon_master = dungeon_master
        self.game_channel_id = game_channel_id
        self.board_channel_id = board_channel_id
        self.command_channel_id = command_channel_id

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected to Discord!')
        self.game_channel = self.bot.get_channel(self.game_channel_id)
        self.board_channel = self.bot.get_channel(self.board_channel_id)
        self.command_channel = self.bot.get_channel(self.command_channel_id)
        await self.send_commands_message(self.command_channel)

    async def send_commands_message(self, ctx):
        pinned_message_exists = False
        for message in await ctx.pins():
            if message.author == self.bot.user and "Commands" in message.content:
                pinned_message_exists = True
                break

        if not pinned_message_exists:
            commands_str = """**Commands:**
            - !select [initials] [row] [column]: Register your selection during pre-game.
            - !setup_game: Create board message and board contents message. Allow selections at this stage (DM only).
            - !start_game: Start the game. Selection not allowed after this point (DM only).
            - !add_square [row] [column]: Add a square to the board (DM only).
            - !remove_square [row] [column]: Remove a square from the board (DM only).
            - !reset_board: Reset the board and user selections (DM only)."""

            commands_message = await ctx.send(commands_str)
            await commands_message.pin()

    @commands.command()
    async def select(self, ctx, initials: str = None, row: int = None, col: int = None):

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

    @commands.command()
    async def setup_game(self, ctx):

        # verify command is only coming from DM and command channel
        if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
            return
        
        # generate and send jpg of bingo square contents to DM channel
        board_contents = self.bot.bingo_helper.generate_bingo_board(self.bingo_squares)
        self.bot.bingo_helper.save_board_as_jpg(board_contents)
        with open('bingo_board.jpg', 'rb') as f:
            picture = discord.File(f)
            await self.board_channel.send(file=picture)

        # generate and send blank emoji board to bingo game channel
        board = [[':white_large_square:' for _ in range(self.bingo_size)] for _ in range(self.bingo_size)]
        board_str = await self.bot.bingo_helper.get_board_display(self.game_channel, board)
        await self.game_channel.send(board_str)
        self.bot.game_save.save_attr(current_board=board)

    @commands.command()
    async def start_game(self, ctx):

        # Verify command is only coming from DM and command channel
        if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
            return

        # Start the game only if it's in pre-game state
        if self.bot.game_save.game_state == 0:
            self.bot.game_save.save_attr(game_state=1)
            await self.game_channel.send("The game has started. No more selections can be made.")
            board_str = await self.bot.bingo_helper.get_board_display(self.game_channel, self.bot.game_save.current_board)
            await self.game_channel.send(board_str)
        else:
            await ctx.send("The game has already started. Use !reset_board to start a new game.")

    @commands.command()
    async def add_square(self, ctx, row: int, col: int):

        # verify command is only coming from DM and command channel
        if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
            return

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

        board_str = await self.bot.bingo_helper.get_board_display(self.game_channel, board)
        await self.game_channel.send(board_str)

        self.bot.game_save.save_attr(current_board=board)

    @commands.command()
    async def remove_square(self, ctx, row: int, col: int):
        # verify command is only coming from DM and command channel
        if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
            return

        board = await self.get_current_board()
        if board is None:
            return

        # set specified square back to white, save, and send
        board[row - 1][col - 1] = ':white_large_square:'
        board_str = await self.bot.bingo_helper.get_board_display(ctx, board)
        await self.game_channel.send(board_str)

        self.bot.game_save.save_attr(current_board=board)

    @commands.command()
    async def reset_board(self, ctx):
        
        # verify command is only coming from DM and command channel
        if ctx.author.id != self.dungeon_master or ctx.channel.id != self.command_channel.id:
            return

        async for message in self.game_channel.history(limit=100):
            if message.author == self.bot.user and ('Bingo Board' in message.content or 'registered' in message.content):
                await message.delete()

        # Clear user selections and winners
        self.bot.game_save.reset()

        await ctx.send("The bingo board and user selections have been reset. You can start a new game using !create_board.")

async def setup(bot):
    await bot.add_cog(BingoCog(bot, COMMAND_CHANNEL_ID, GAME_CHANNEL_ID, BOARD_CHANNEL_ID, DUNGEON_MASTER, BINGO_SIZE, bingo_squares))