import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

# Constants
API_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
LOGS_FOLDER = 'export'
PROFILE_FOLDER = os.path.join(LOGS_FOLDER, 'profiles')
INDEX_FILE_PATH = os.path.join(LOGS_FOLDER, 'index.html')

# Ensure folders exist
os.makedirs(PROFILE_FOLDER, exist_ok=True)

# Create an index.html file if it doesn't exist
if not os.path.exists(INDEX_FILE_PATH):
    with open(INDEX_FILE_PATH, 'w', encoding='utf-8') as index_file:
        index_file.write(
            '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="UTF-8">\n'
            '\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '\t\t<title>Document</title>\n\t</head>\n\n\t<body>\n\t\t<!-- Messages will be appended below -->\n\t</body>\n</html>'
        )


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents, description='Chat Export Bot')

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')


def append_to_html(content: str):
    """Append content right before the closing </body> tag in index.html"""
    with open(INDEX_FILE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the last </body> tag
    for i in range(len(lines) - 1, -1, -1):
        if '</body>' in lines[i]:
            lines.insert(i, f'{content}\n')  # Indent messages properly
            break

    # Write back to the file
    with open(INDEX_FILE_PATH, 'w', encoding='utf-8') as file:
        file.writelines(lines)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    log_entry = f"\t\t<p><strong>{message.author.name}:</strong> {message.content}</p>"

    # Print to terminal
    print(message.content, message.attachments, message.author.id, message.author.name, message.author.display_avatar.url)

    # Append to index.html before the closing </body> tag
    append_to_html(log_entry)


bot.run(API_TOKEN)
