from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
from api.auth import get_current_user
from api.config import settings
from api import models
from sqlalchemy import select
from api.db import AsyncSessionLocal
import json
import asyncio

router = APIRouter(prefix="/api/ws", tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        # user_id -> set of active WebSockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            to_remove = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    to_remove.add(connection)
            for c in to_remove:
                self.active_connections[user_id].discard(c)

manager = ConnectionManager()

# We need a token in query parameter for WebSocket auth
async def get_user_from_token(token: str) -> models.User | None:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload = parts[1]
        import base64
        payload_pad = payload + '=' * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload_pad))
        user_id = data.get("sub")
        if not user_id:
            return None
            
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(models.User).where(models.User.id == int(user_id)))
            return result.scalar_one_or_none()
    except Exception:
        return None

@router.websocket("/progress")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
