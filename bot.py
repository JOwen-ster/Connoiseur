import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
API_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
BASE_DIR = os.path.dirname(__file__)
EXPORT_FOLDER = os.path.join(BASE_DIR, 'export')
INDEX_FILE_PATH = os.path.join(EXPORT_FOLDER, 'index.html')


def ensure_directory_and_file():
    """Ensure the export directory and index.html file exist."""
    os.makedirs(EXPORT_FOLDER, exist_ok=True)  # Create the directory if missing

    if not os.path.exists(INDEX_FILE_PATH):  # Create the file if missing
        with open(INDEX_FILE_PATH, 'w', encoding='utf-8') as file:
            file.write(
                '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="UTF-8">\n'
                '\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '\t\t<title>Document</title>\n\t</head>\n\n\t<body>\n\t\t<!-- Messages -->\n\t</body>\n</html>'
            )
        print(f"Created file: {INDEX_FILE_PATH}")
    else:
        print(f"File already exists: {INDEX_FILE_PATH}")


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
    ensure_directory_and_file()
    # Read existing content and set file pointer to the end using 'r'
    with open(INDEX_FILE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the last </body> tag and insert content
    for i in reversed(range(len(lines))):
        if '</body>' in lines[i]:
            lines.insert(i, f'{content}\n')
            break

    # Write updated content back
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
