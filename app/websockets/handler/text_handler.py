import base64
from app.LLM.ollama_llms import Assistant
from app.websockets.manager import manager

assistant = Assistant()

async def handle_text(text: str, client_id: str):
    async def send_text(text_chunk):
        await manager.send_to_user(client_id, {"type": "text", "data": text_chunk})
        
    async def send_audio(audio_chunk):
        encoded_audio = base64.b64encode(audio_chunk).decode('utf-8')
        await manager.send_to_user(client_id, {"type": "audio", "data": encoded_audio})

    await assistant.chat_stream(text, send_text, send_audio)