import sys
import re
import asyncio
import edge_tts
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from app.LLM.personality.friday_personality import personality
import emoji

class Assistant:
    def __init__(self, model_name="llama3.2:1b", temperature=0.5, voice="en-US-JennyNeural", rate="+20%"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )
        self.voice = voice
        self.rate = rate



    async def chat_stream(self, user_prompt: str, text_cb, audio_cb):
        """Streams the LLM response (text) and TTS (audio) asynchronously via callbacks."""
        messages = [
            SystemMessage(content=personality),
            HumanMessage(content=user_prompt)
        ]
        
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
            print(f"Error in LLM stream: {e}")
            
        await audio_queue.put(None)
        await tts_task
