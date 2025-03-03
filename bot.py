import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
API_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
BASE_DIR = os.path.dirname(__file__)
EXPORT_FOLDER = os.path.join(BASE_DIR, 'export')

# message.guild.id: {message.channel.id: str} WHERE str = HTML File Content
logged_guilds: dict[int, dict[int, str]] = {}

def format_guild_directory_name(messageObject):
    return os.path.join(EXPORT_FOLDER, f'guild-{messageObject.guild.name}')


def format_index_filename(messageObject):
    return os.path.join(format_guild_directory_name(messageObject=messageObject), f'channel-{messageObject.channel.name}.html')

def ensure_directory_and_file(messageObject=None):
    """Ensure the export directory and index.html file exist."""
    guild_dir = format_guild_directory_name(messageObject=messageObject)
    index_location = format_index_filename(messageObject=messageObject)
    
    os.makedirs(EXPORT_FOLDER, exist_ok=True)  # Create the directory if missing
    os.makedirs(guild_dir, exist_ok=True)
    if not os.path.exists(index_location):  # Create the file if missing
        with open(index_location, 'w', encoding='utf-8') as file:
            file.write(
                '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="UTF-8">\n'
                '\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '\t\t<title>Document</title>\n\t</head>\n\n\t<body>\n\t\t<!-- Messages -->\n\t</body>\n</html>'
            )
        print(f"Created file: {index_location}")
    else:
        print(f"File already exists: {index_location}")


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='^', intents=intents, description='Chat Export Bot')


@bot.event
async def on_ready():
    botTree = await bot.tree.sync()
    print(f'Synced {len(botTree)} commands')
    print(f'Logged in as {bot.user.name}')


def append_to_html(content: str, messageObject: discord.Message=None):
    """Append content right before the closing </body> tag in index.html"""
    ensure_directory_and_file(messageObject=messageObject)
    
    guild_dir = format_guild_directory_name(messageObject=messageObject)
    index_location = format_index_filename(messageObject=messageObject)
    
    # Read existing content and set file pointer to the end using 'r'
    with open(index_location, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the last </body> tag and insert content
    for i in reversed(range(len(lines))):
        if '</body>' in lines[i]:
            lines.insert(i, f'{content}\n')
            break

    # Write updated content back
    with open(index_location, 'w', encoding='utf-8') as file:
        file.writelines(lines)


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

    # Append to index.html before the closing </body> tag
    append_to_html(content=log_entry, messageObject=message)


bot.run(API_TOKEN)
