import json
from collections import defaultdict

from fastapi import WebSocket


class WSConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                self._connections.pop(user_id, None)

    async def broadcast(self, user_id: int, payload: dict) -> None:
        for ws in list(self._connections.get(user_id, set())):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                self.disconnect(user_id, ws)


ws_manager = WSConnectionManager()
