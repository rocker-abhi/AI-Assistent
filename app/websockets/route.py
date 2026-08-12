from app.websockets.shema.input_schema import InputMessageSchema
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager
from app.core.logger import logger
from app.websockets.handler.text_handler import handle_text
from app.websockets.shema.input_schema import InputMessageSchema

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time communication with the frontend.
    """
    # Attempt to accept and register the connection via our singleton manager
    connected = await manager.connect(client_id, websocket)
    
    # If the manager rejected the connection (e.g., another connection already exists), exit
    if not connected:
        return

    try:
        while True:
            # Wait for incoming messages from the frontend
            raw_data = await websocket.receive_text()
            data = InputMessageSchema.model_validate_json(raw_data)
            logger.info(f"[WebSocketRoute] Received message from {client_id}: {data}")
            
            # TODO: Handle AI processing, signaling, or commands here
            
            # Example echo response to confirm receipt
            await manager.send_to_user(client_id, {"status": "received", "message": data.model_dump(mode='json')})
            if data.message_type == "text":
                handle_text(data.content)

    except WebSocketDisconnect:
        # Handle client disconnection normally
        manager.disconnect(client_id)
        logger.info(f"[WebSocketRoute] Client {client_id} disconnected cleanly.")
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"[WebSocketRoute] Unexpected error in websocket communication: {e}")
        manager.disconnect(client_id)
