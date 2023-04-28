# role-bot
DND BINGO! The blind bingo game where your actions fill in the board.

## TECHNOLOGIES
This is a discord bot that you can add to your server by entering an API token into the config/bingo_config.py file
Python 3.10.11

## RULES:
- Only the DM can see the board contents. The squares are filled from the list in bingo_squares.py file and are events that can occur throughout a DND/PF2E playthrough. Feel free to add your own here when you clone the repository. Be specific to your party if you want even more fun.
- Each player at the beginning of the session selects a row and column.
- If their row or column fills up before the end of the session, they win!
- This allows for multiple winners. You decide the prize. (hero point or something in game or a candy bar idk :) )
- That's it!

## Prerequisites
- Docker installed on your machine. You can download and install Docker from the [official website](https://www.docker.com/products/docker-desktop/).
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

## Quickstart
### 1. Pull the Docker image
Open a terminal or command prompt and run the following command to pull the Role Bot Docker image from Docker Hub:

```
docker pull jblackburn86/role_bot:latest
```

### 2. Prepare the configuration files
Create a new folder on your local machine to store the configuration files. Inside this folder, create the following files:

bingo_config.yaml: This file will contain your Discord bot token, channel IDs, user ID, bingo size, and other settings. Use the example file provided in this repository (bot/config/bingo_config_example.yaml) as a reference.
bingo_squares.yaml: This file will contain the bingo squares. Use the example file provided in this repository (bot/config/bingo_squares_example.yaml) as a reference.
Make sure to replace the placeholders in the bingo_config.yaml file with your actual Discord bot token, channel IDs, user ID, and other settings.

### 3. Run the Docker container
In the terminal or command prompt, run the following command to start the Role Bot Docker container:

```
docker run -d --name role_bot -v /path/to/your/config/folder:/app/bot/config jblackburn/role_bot:latest
```
Replace /path/to/your/config/folder with the path to the folder you created in step 2.

The -v flag maps the local configuration folder to the /app/bot/config folder inside the Docker container, allowing the bot to access the configuration files.

### 4. Invite the bot to your Discord server
Follow the instructions in the Discord Developer Portal to invite your bot to your server.

Updating the bot
To update the bot to the latest version, simply stop the running container, pull the latest image, and start a new container with the updated image:

```
docker stop role_bot
docker rm role_bot
docker pull jblackburn/role_bot:latest
docker run -d --name role_bot -v /path/to/your/config/folder:/app/bot/config jblackburn86/role_bot:latest
```
Replace /path/to/your/config/folder with the path to the folder you created in step 2.

## BOT PERMISSIONS:
  - Manage Channels: To create and manage game channels
  - Manage Messages: To delete and pin messages in the game channels
  - Read Messages: To receive commands from users
  - Send Messages: To send messages and respond to commands
  - Attach Files: To generate and send Bingo board images
  
## COMMANDS:
- !select [initials] [row] [column]: Register your selection during pre-game.
- !setup_game: Create board message and board contents message. Allow selections at this stage (DM only).
- !start_game: Start the game. Selection not allowed after this point (DM only).
- !add_square [row] [column]: Add a square to the board (DM only).
- !remove_square [row] [column]: Remove a square from the board (DM only).
- !reset_game: Reset the board and user selections (DM only).
