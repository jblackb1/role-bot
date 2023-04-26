# role-bot
DND BINGO!

RULES:
- Only the DM can see the board contents. The squares are filled from the bingo_squares.py file and are events that can occur throughout a PF2E playthrough.
- Each player at the beginning of the session selects a row and column.
- If their row or column fills up before the end of the session, they win!
- This allows for multiple winners. You decide the prize. (hero point or something in game or a candy bar idk)
- That's it!

SETUP:
- pip install discord.py
- copy bingo_config_example.py to bingo_config.py
- create 3 new channels in your discord server:
  - One for the board display and player row/col selections.
  - One for bingo board contents (should be private to only dungeon master and the bot)
  - One for commands from DM like filling squares, starting/resetting game (should be private to only dungeon master and the bot)

BOT PERMISSIONS:
  - add here...
  
COMMANDS:
- !select [initials] [row] [column]: Register your selection during pre-game.
- !setup_game: Create board message and board contents message. Allow selections at this stage (DM only).
- !start_game: Start the game. Selection not allowed after this point (DM only).
- !add_square [row] [column]: Add a square to the board (DM only).
- !remove_square [row] [column]: Remove a square from the board (DM only).
- !reset_board: Reset the board and user selections (DM only).
