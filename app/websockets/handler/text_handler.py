import base64
import asyncio
from app.LLM.groq_llms import Assistant
from app.websockets.manager import manager
from app.core.database import Database
from app.models.chat_schema.conversation import Conversation
from app.models.chat_schema.message import Message
from app.core.logger import logger
from app.core.config import settings

assistant = Assistant()

async def handle_text(text: str, client_id: str):
    db = Database().get_session()
    try:
        from sqlalchemy.orm import selectinload
        conversation = db.query(Conversation).options(selectinload(Conversation.messages)).filter(Conversation.is_primary_chat == True).first()
        if not conversation:
            conversation = Conversation(is_primary_chat=True, title="Primary Chat")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        history = conversation.messages[-settings.MAX_HISTORY_MESSAGES:] if getattr(conversation, 'messages', None) else []

        user_msg = Message(conversation_id=conversation.id, role="user", content=text)
        db.add(user_msg)
        db.commit()
        logger.info(f"[TextHandler] User message saved: {text}")

        full_response = []

        async def send_text(text_chunk):
            full_response.append(text_chunk)
            await manager.send_to_user(client_id, {"type": "text", "data": text_chunk})
            
        async def send_audio(audio_chunk):
            encoded_audio = base64.b64encode(audio_chunk).decode('utf-8')
            await manager.send_to_user(client_id, {"type": "audio", "data": encoded_audio})
            
        await assistant.chat_stream(text, send_text, send_audio, history=history)
        
        assistant_content = "".join(full_response)
        assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=assistant_content)
        db.add(assistant_msg)
        db.commit()
        logger.info(f"[TextHandler] Assistant message saved: {assistant_content}")

    except asyncio.CancelledError:
        logger.info("[TextHandler] Processing cancelled.")
        assistant_content = "".join(full_response)
        if assistant_content:
            assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=assistant_content)
            db.add(assistant_msg)
            db.commit()
            logger.info(f"[TextHandler] Assistant message saved (partial): {assistant_content}")
        raise
    except Exception as e:
        logger.error(f"[TextHandler] Error handling text: {e}")
        db.rollback()
    finally:
        db.close()
        
    await manager.send_to_user(client_id, {"type": "done"})