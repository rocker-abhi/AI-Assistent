import re
import asyncio
import edge_tts
import emoji
from typing import Optional, List, Callable, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from app.LLM.personality.friday_personality import personality
from app.core.config import settings
from app.core.logger import logger

async def _invoke_callback(cb: Optional[Callable], *args):
    """Helper to safely invoke synchronous or asynchronous callback functions."""
    if cb is None:
        return
    res = cb(*args)
    if asyncio.iscoroutine(res) or asyncio.isfuture(res):
        await res

class Assistant:
    """
    Unified AI Assistant engine supporting dynamic switching between LLM providers (Groq / Ollama)
    via configuration with real-time text streaming and Edge-TTS voice generation.
    """
    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        voice: Optional[str] = None,
        rate: Optional[str] = None
    ):
        self.provider = (provider or settings.LLM_PROVIDER or "groq").strip().lower()
        self.voice = voice or settings.TTS_VOICE
        self.rate = rate or settings.TTS_RATE

        if self.provider == "ollama":
            selected_model = model_name or settings.OLLAMA_MODEL
            selected_temp = temperature if temperature is not None else settings.OLLAMA_TEMPERATURE
            logger.info(f"[Assistant] Initializing Ollama provider (model: {selected_model}, base_url: {settings.OLLAMA_BASE_URL})...")
            self.llm = ChatOllama(
                model=selected_model,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=selected_temp
            )
        else:
            # Default to Groq
            selected_model = model_name or settings.GROQ_MODEL
            selected_temp = temperature if temperature is not None else settings.GROQ_TEMPERATURE
            logger.info(f"[Assistant] Initializing Groq provider (model: {selected_model})...")
            self.llm = ChatGroq(
                model=selected_model,
                temperature=selected_temp,
                api_key=settings.GROQ_API_KEY
            )

    async def chat_stream(
        self,
        user_prompt: str,
        text_cb: Callable[[str], Any],
        audio_cb: Callable[[bytes], Any],
        history: Optional[List[Any]] = None
    ):
        """
        Streams the LLM response (text) and TTS (audio) asynchronously via callbacks.
        """
        messages = [
            SystemMessage(content=personality),
        ]

        if history:
            for msg in history:
                if getattr(msg, "role", None) == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif getattr(msg, "role", None) == "assistant":
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
                            await _invoke_callback(audio_cb, audio_data)
                    except Exception as tts_err:
                        logger.debug(f"[Assistant TTS] Chunk error: {tts_err}")
                audio_queue.task_done()

        tts_task = asyncio.create_task(tts_worker())

        buffer = ""
        try:
            async for chunk in self.llm.astream(messages):
                text = chunk.content
                if text:
                    await _invoke_callback(text_cb, text)
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
            logger.error(f"[Assistant] Error in LLM ({self.provider}) stream: {e}")
            raise

        finally:
            await audio_queue.put(None)
            await tts_task
