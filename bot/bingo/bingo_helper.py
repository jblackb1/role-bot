import random
import textwrap
from PIL import Image, ImageDraw, ImageFont


class BingoHelper:
    def __init__(self, bot, filename='../bingo_board.jpg', font_path = 'C:\\Windows\\Fonts\\courbd.ttf'):
        self.bot = bot
        self.filename = filename
        self.font_path = font_path

    def generate_bingo_board(self, squares):
        board = []
        selected_squares = random.sample(squares, 25)
        for i in range(5):
            row = selected_squares[i*5:(i+1)*5]
            board.append(row)
        return board

    def draw_text(self, draw, text, font, position, max_width):
        lines = textwrap.wrap(text, width=max_width)
        x, y = position
        for line in lines:
            draw.text((x, y), line, font=font, fill='black')
            y += font.getsize(line)[1]

    def save_board_as_jpg(self, board):
        font = ImageFont.truetype(self.font_path, 24)
        padding = 10
        cell_width, cell_height = font.getsize("X" * 25)[0] + 2 * padding, font.getsize("X")[1] * 5 + 2 * padding
        img_width, img_height = cell_width * 5, cell_height * 5

        img = Image.new('RGB', (img_width, img_height), color='white')
        d = ImageDraw.Draw(img)

        for i, row in enumerate(board):
            for j, square in enumerate(row):
                x, y = j * cell_width, i * cell_height
                d.rectangle([(x, y), (x + cell_width, y + cell_height)], outline='black')
                self.draw_text(d, square, font, (x + padding, y + padding), max_width=25)

        img.save(self.filename)

    async def get_board_display(self, ctx, board):
        # Format the board string
        board_rows = [' '.join(row) for row in board]
        board_str = f'{"IN PROGRESS" if self.bot.game_save.game_state == 1 else "PRE-GAME"}\nBingo Board:\n' + '\n'.join(board_rows)

        # Add selections to the board
        selections_text = "Selections:\n"
        for user_id, selections in self.bot.game_save.selections.items():
            row, col = selections['row'], selections['col']
            initials = selections['initials']
            member = ctx.guild.get_member(user_id)
            if member is not None:
                selections_text += f'{initials}: row {row+1}, col {col+1}\n'

        # Add winners to the board
        winners_text = 'Winners: ' + ', '.join([f'<@{winner_id}>' for winner_id in self.bot.game_save.winners])

        # Combine all parts of the board string
        board_str += '\n\n' + selections_text + '\n' + winners_text

        existing_board_message = None
        async for message in ctx.history(limit=100):
            if message.author == self.bot.user and 'Bingo Board' in message.content:
                existing_board_message = message
                break

        if existing_board_message:
            await existing_board_message.delete()
            
        return board_str

    def check_winners(self, board, bingo_size):
        current_winners = set(self.bot.game_save.winners)
        new_winners = set()
        
        for member, selections in self.bot.game_save.selections.items():
            row, col = selections['row'], selections['col']
            if all([square == ':black_large_square:' for square in board[row]]) or all([board[i][col] == ':black_large_square:' for i in range(bingo_size)]):
                new_winners.add(member)
        
        # Find the difference between the new winners and the current winners
        winners_diff = new_winners - current_winners

        # Update the game_save.winners list with the new winners
        self.bot.game_save.save_attr(winners=list(new_winners))

        return winners_diff

    def get_current_board(self):
        return self.bot.game_save.current_board