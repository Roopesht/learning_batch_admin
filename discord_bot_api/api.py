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
