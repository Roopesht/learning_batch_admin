#!/bin/bash
set -e

# ===== PROJECT 1: discord_bot_api =====
mkdir -p discord_bot_api && cd discord_bot_api

# --- requirements.txt ---
cat > requirements.txt <<'EOF'
discord.py==2.3.2
fastapi==0.110.0
uvicorn[standard]==0.29.0
python-dotenv==1.0.0
EOF

# --- .env template ---
cat > .env <<'EOF'
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
EOF

# --- bot.py ---
cat > bot.py <<'EOF'
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
EOF

# --- api.py ---
cat > api.py <<'EOF'
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from bot import bot, create_thread_with_message, TOKEN
import uvicorn

app = FastAPI()

class ThreadRequest(BaseModel):
    channel_id: int
    thread_name: str
    message_content: str

@app.post("/create_thread")
async def create_thread(req: ThreadRequest):
    try:
        thread = await create_thread_with_message(req.channel_id, req.thread_name, req.message_content)
        return {"status": "success", "thread_id": thread.id, "thread_name": thread.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(TOKEN))

if __name__ == "__main__":
    start_bot()
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
EOF

cd ..

# ===== PROJECT 2: nicegui_admin =====
mkdir -p nicegui_admin && cd nicegui_admin

# --- requirements.txt ---
cat > requirements.txt <<'EOF'
nicegui==1.4.10
python-dotenv==1.0.0
requests==2.31.0
EOF

# --- .env template ---
cat > .env <<'EOF'
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
DISCORD_API_URL=http://localhost:8000/create_thread
EOF

# --- batches.json ---
cat > batches.json <<'EOF'
[
  {"batch": "Batch-1", "type": "assignments", "channelid": 111111111111111111},
  {"batch": "Batch-2", "type": "sessions", "channelid": 222222222222222222},
  {"batch": "Batch-3", "type": "general-discussion", "channelid": 333333333333333333}
]
EOF

# --- services/gemini.py ---
mkdir -p services
cat > services/gemini.py <<'EOF'
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")

def get_response(system_message: str, user_message: str, model="gemini-2.0-flash") -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_message}\n\nUser: {user_message}"}]}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
EOF

# --- main.py ---
cat > main.py <<'EOF'
import json
import os
import requests
from nicegui import ui
from services import gemini
from dotenv import load_dotenv

load_dotenv()
DISCORD_API_URL = os.getenv("DISCORD_API_URL", "http://localhost:8000/create_thread")

# Load batch/type data
with open('batches.json', 'r') as f:
    batch_data = json.load(f)

batches = sorted({entry["batch"] for entry in batch_data})
types = sorted({entry["type"] for entry in batch_data})

def find_channel_id(batch_selection, type_selection):
    for entry in batch_data:
        if entry["batch"] in batch_selection and entry["type"] == type_selection:
            return entry["channelid"]
    return None

class ThreadCreatorScreen:
    def __init__(self):
        with ui.column().classes('w-full p-4 gap-4'):
            ui.label('Create Discord Threads').classes('text-2xl font-bold')
            ui.separator()

            with ui.row().classes('w-full gap-4'):
                self.batch_select = ui.select(batches, multiple=True, label='Select Batch(es)')
                self.type_select = ui.select(types, label='Select Type')
            
            self.thread_name_input = ui.input('Thread Name').classes('w-full')
            self.message_content_input = ui.textarea('Message Content').props('rows=5').classes('w-full')
            
            ui.button('Create Thread', on_click=self.create_thread).classes('bg-blue-500 text-white w-40')

    async def create_thread(self):
        selected_batches = self.batch_select.value or []
        selected_type = self.type_select.value
        thread_name = self.thread_name_input.value or ''
        message_content = self.message_content_input.value or ''
        
        if not selected_batches or not selected_type or not thread_name or not message_content:
            ui.notify('Please fill all fields', color='negative')
            return
        
        # Rephrase message content using Gemini
        system_msg = "Rephrase the following message to sound structured, concise and professional."
        rephrased_message = gemini.get_response(system_msg, message_content)
        
        # Create threads for each selected batch
        for batch in selected_batches:
            channel_id = find_channel_id([batch], selected_type)
            if not channel_id:
                ui.notify(f"No channel ID found for {batch} - {selected_type}", color='negative')
                continue
            
            try:
                payload = {
                    "channel_id": channel_id,
                    "thread_name": thread_name,
                    "message_content": rephrased_message
                }
                response = requests.post(DISCORD_API_URL, json=payload, timeout=10)
                result = response.json()
                if result.get("status") == "success":
                    ui.notify(f"Thread '{thread_name}' created for {batch}", color='positive')
                else:
                    ui.notify(f"Error creating thread for {batch}: {result.get('message')}", color='negative')
            except Exception as e:
                ui.notify(f"Error: {e}", color='negative')

def main():
    with ui.left_drawer().classes('bg-gray-100 p-4'):
        ui.label('Menu').classes('text-lg font-bold')
        ui.link('Thread Creator', '/')
        ui.separator()

    with ui.header().classes('bg-blue-100 p-2'):
        ui.label('Online Training Admin Panel').classes('text-xl font-bold')

    with ui.footer().classes('bg-gray-100 p-2'):
        ui.label('Ojasa Mirai Training System © 2025')

    @ui.page('/')
    def home():
        ThreadCreatorScreen()

    ui.run(reload=False)

if __name__ == '__main__':
    main()
EOF

cd ..
echo "Both projects created successfully!"