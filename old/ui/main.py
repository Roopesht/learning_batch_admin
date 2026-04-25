import asyncio
import json
from nicegui import ui
from services import discord_bot, gemini

# Load batch/type data
with open('batches.json', 'r') as f:
    batch_data = json.load(f)

batches = sorted({entry["batch"] for entry in batch_data})
types = sorted({entry["type"] for entry in batch_data})

# Helper to map selection to channel_id
def find_channel_id(batch_selection, type_selection):
    for entry in batch_data:
        if entry["batch"] in batch_selection and entry["type"] == type_selection:
            batchid = entry["channelid"]
            print (entry["channelid"])
            return batchid
    return None

class ThreadCreatorScreen:
    def __init__(self):
        with ui.column().classes('w-full'):
            ui.label('Create Discord Threads').classes('text-2xl font-bold')
            ui.separator()

            with ui.row().classes('w-full'):
                self.batch_select = ui.select(batches, multiple=True, label='Select Batch(es)')
                self.type_select = ui.select(types, label='Select Type')
            
            self.thread_name_input = ui.input('Thread Name')
            self.message_content_input = ui.textarea('Message Content').props('rows=5')
            
            ui.button('Create Thread', on_click=self.create_thread).classes('bg-blue-500 text-white')

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
                thread = await discord_bot.create_thread_with_message(channel_id, thread_name, rephrased_message)
                ui.notify(f"Thread '{thread.name}' created for {batch}", color='positive')
            except Exception as e:
                ui.notify(f"Error creating thread for {batch}: {e}", color='negative')

def main():
    with ui.left_drawer().classes('bg-gray-100'):
        ui.label('Menu').classes('text-lg font-bold')
        ui.link('Thread Creator', '/')
        ui.separator()

    with ui.header().classes('bg-blue-100'):
        ui.label('Online Training Admin Panel').classes('text-xl font-bold')

    with ui.footer().classes('bg-gray-100'):
        ui.label('Ojasa Mirai Training System © 2025')

    @ui.page('/')
    def home():
        ThreadCreatorScreen()

    # Start Discord bot in background
    asyncio.ensure_future(discord_bot.bot.start(discord_bot.TOKEN))
    ui.run(reload=False)

if __name__ == '__main__':
    main()
