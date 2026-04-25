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
        rephrased_message = message_content #gemini.get_response(system_msg, message_content)
        
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
