import discord
from discord.ext import commands
import os
import aiofiles  # Import aiofiles for async file handling
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
BASE_DIR = os.path.dirname(__file__)
EXPORT_FOLDER = os.path.join(BASE_DIR, 'export')

logged_guilds: dict[int, dict[int, str]] = {}


def format_guild_directory_name(messageObject):
    return os.path.join(EXPORT_FOLDER, f'guild-{messageObject.guild.name}')


def format_index_filename(messageObject):
    return os.path.join(format_guild_directory_name(messageObject), f'channel-{messageObject.channel.name}.html')


async def ensure_directory_and_file(messageObject=None):
    """Ensure the export directory and index.html file exist."""
    guild_dir = format_guild_directory_name(messageObject)
    index_location = format_index_filename(messageObject)

    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    os.makedirs(guild_dir, exist_ok=True)

    if not os.path.exists(index_location):
        async with aiofiles.open(index_location, 'w', encoding='utf-8') as file:
            await file.write(
                '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="UTF-8">\n'
                '\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '\t\t<title>Document</title>\n\t</head>\n\n\t<body>\n\t\t<!-- Messages -->\n\t</body>\n</html>'
            )
        print(f"Created file: {index_location}")
    else:
        print(f"File already exists: {index_location}")


async def append_to_html(content: str, messageObject: discord.Message = None):
    """Append content right before the closing </body> tag in index.html asynchronously"""
    await ensure_directory_and_file(messageObject)

    index_location = format_index_filename(messageObject)

    # Read the file asynchronously
    async with aiofiles.open(index_location, 'r', encoding='utf-8') as file:
        lines = await file.readlines()

    # Insert new content before the last </body> tag
    for i in reversed(range(len(lines))):
        if '</body>' in lines[i]:
            lines.insert(i, f'{content}\n')
            break

    # Write updated content back asynchronously
    async with aiofiles.open(index_location, 'w', encoding='utf-8') as file:
        await file.writelines(lines)


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents, description='Chat Export Bot')


@bot.event
async def on_ready():
    botTree = await bot.tree.sync()
    print(f'Synced {len(botTree)} commands')
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild.id not in logged_guilds:
        logged_guilds[message.guild.id] = {}

    if message.channel.id not in logged_guilds[message.guild.id]:
        logged_guilds[message.guild.id][message.channel.id] = ''

    log_entry = f"\t\t<p><strong>{message.author.name}:</strong> {message.content}</p>"

    # Print to terminal
    print(message.content, message.attachments, message.author.id, message.author.name, message.author.display_avatar.url)

    # Append to index.html asynchronously
    await append_to_html(content=log_entry, messageObject=message)


bot.run(API_TOKEN)
