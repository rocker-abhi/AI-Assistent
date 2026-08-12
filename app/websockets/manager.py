from typing import Dict
from fastapi import WebSocket
from app.core.logger import logger

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.active_connections: Dict[str, WebSocket] = {}
            logger.info(f"[{cls.__name__}] Initialized singleton instance")
        return cls._instance

    async def connect(self, user_id: str, websocket: WebSocket):
        if len(self.active_connections) >= 1:
            logger.warning(f"[{self.__class__.__name__}] Stale connection detected. Evicting old connection for {user_id}.")
            for old_id, old_ws in list(self.active_connections.items()):
                try:
                    await old_ws.close(code=1000, reason="Replaced by new connection")
                except Exception:
                    pass
                self.active_connections.pop(old_id, None)
            
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"[{self.__class__.__name__}] User connected: {user_id}")
        return True

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        logger.info(f"[{self.__class__.__name__}] User disconnected: {user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)
        else:
            logger.warning(f"[{self.__class__.__name__}] Cannot send to {user_id}: Not connected")

    async def broadcast(self, message: dict):
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error broadcasting to {user_id}: {e}")
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(user_id)

    def get_connection_count(self) -> int:
        return len(self.active_connections)

manager = ConnectionManager()