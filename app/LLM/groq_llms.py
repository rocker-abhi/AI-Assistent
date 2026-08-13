import sys
import re
import asyncio
import edge_tts
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from app.LLM.personality.friday_personality import personality
from app.core.config import settings
from app.core.logger import logger
import emoji

class Assistant:
    def __init__(self, model_name=None, temperature=None, voice=None, rate=None):
        self.llm = ChatGroq(
            model=settings.GROK_MODEL,
            temperature=0.2,
            api_key=settings.GROK_API_KEY
        )
        self.voice = voice or settings.TTS_VOICE
        self.rate = rate or settings.TTS_RATE

    async def chat_stream(self, user_prompt: str, text_cb, audio_cb, history=None):
        """Streams the LLM response (text) and TTS (audio) asynchronously via callbacks."""
        messages = [
            SystemMessage(content=personality),
        ]
        
        if history:
            for msg in history:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
                    
        messages.append(HumanMessage(content=user_prompt))
        
        audio_queue = asyncio.Queue()
        
        async def tts_worker():
            while True:
                sentence = await audio_queue.get()
                if sentence is None:
                    break
                clean_sentence = emoji.replace_emoji(sentence, replace="").replace("*", "").strip()
                if clean_sentence:
                    communicate = edge_tts.Communicate(clean_sentence, self.voice, rate=self.rate)
                    try:
                        audio_data = b""
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                audio_data += chunk["data"]
                        if audio_data:
                            await audio_cb(audio_data)
                    except Exception:
                        pass
                audio_queue.task_done()

        tts_task = asyncio.create_task(tts_worker())

        buffer = ""
        try:
            async for chunk in self.llm.astream(messages):
                text = chunk.content
                if text:
                    await text_cb(text)
                    buffer += text
                    
                    match = re.search(r'(?<=[.,!?:;])[\s\n]+', buffer)
                    if match:
                        split_idx = match.end()
                        sentence = buffer[:split_idx]
                        await audio_queue.put(sentence)
                        buffer = buffer[split_idx:]

            if buffer.strip():
                await audio_queue.put(buffer.strip())
        except Exception as e:
            logger.error(f"Error in LLM stream: {e}")
            
        await audio_queue.put(None)
        await tts_task
