import os
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
bot = discord.Client(intents=intents)

async def create_thread_with_message(channel_id: int, thread_name: str, message_content: str, auto_archive: int = 1440):
    channel = bot.get_channel(channel_id)
    #bot.get_guild(1404494048936591390)
    if not channel:
        raise ValueError("Channel not found or bot has no access.")
    
    guild = bot.get_guild(1404494048936591390)
    msg = await channel.send(message_content)
    thread = await msg.create_thread(name=thread_name, auto_archive_duration=auto_archive)
    return thread

def start_discord_bot():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(bot.start(TOKEN), loop=loop)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user} (ID: {bot.user.id})')
    print('Connected to these guilds:')
    for g in bot.guilds:
        print(f'- {g.name} (ID: {g.id})')