import base64
import numpy as np
import whisper
import asyncio
from app.core.logger import logger
from app.websockets.handler.text_handler import handle_text
from app.websockets.manager import manager
from app.core.config import settings

_whisper_model_instance = None

def get_whisper_model():
    global _whisper_model_instance
    if _whisper_model_instance is None:
        logger.info(f"[AudioHandler] Loading Whisper model ({settings.WISPER_MODEL})...")
        _whisper_model_instance = whisper.load_model(settings.WISPER_MODEL)
        logger.info("[AudioHandler] Whisper model loaded successfully.")
    return _whisper_model_instance

async def handle_audio(audio_base64: str, client_id: str):
    """
    Receives base64 encoded raw Float32 audio samples (16000Hz).
    Transcribes it with Whisper, then forwards the text to handle_text.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
        
        # Convert bytes to numpy float32 array
        audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
        
        model = get_whisper_model()
        
        loop = asyncio.get_running_loop()
        logger.info("[AudioHandler] Starting Whisper transcription...")
        
        # Run synchronous transcription in a thread pool to avoid blocking the event loop
        result = await loop.run_in_executor(None, lambda: model.transcribe(audio_np))
        
        transcribed_text = result.get("text", "").strip()
        logger.info(f"[AudioHandler] Transcription result: {transcribed_text}")
        
        if not transcribed_text:
            logger.info("[AudioHandler] No text detected, ignoring.")
            # Notify frontend that nothing was captured, but we are done processing the audio
            await manager.send_to_user(client_id, {"type": "done"})
            return
            
        # Hand off to the text handler to generate the AI response
        await handle_text(transcribed_text, client_id)
        
    except asyncio.CancelledError:
        logger.info("[AudioHandler] Transcription cancelled.")
        raise
    except Exception as e:
        logger.error(f"[AudioHandler] Error handling audio: {e}")
        await manager.send_to_user(client_id, {"type": "done"})
