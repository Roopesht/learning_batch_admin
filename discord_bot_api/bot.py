import os
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
print ("token: ", TOKEN)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
bot = discord.Client(intents=intents)

async def create_thread_with_message(channel_id: int, thread_name: str, message_content: str, auto_archive: int = 1440):
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    if not channel:
        raise ValueError("Channel not found or bot has no access.")
    msg = await channel.send(message_content)
    thread = await msg.create_thread(name=thread_name, auto_archive_duration=auto_archive)
    return thread

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user} (ID: {bot.user.id})')
    for g in bot.guilds:
        print(f'- {g.name} (ID: {g.id})')
