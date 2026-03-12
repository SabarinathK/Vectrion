import asyncio

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.common.config import get_settings
from app.common.security import decode_token
from app.common.ws import ws_manager
from app.platform.db.session import init_db
from app.platform.events.pubsub import subscribe_events

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    app.state.event_task = asyncio.create_task(_event_forwarder())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    task = getattr(app.state, "event_task", None)
    if task:
        task.cancel()


async def _event_forwarder() -> None:
    async for event in subscribe_events():
        user_id = int(event.get("user_id", 0))
        if user_id:
            await ws_manager.broadcast(user_id, event)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.websocket("/api/v1/ws/notifications")
async def ws_notifications(websocket: WebSocket, token: str = Query(...)) -> None:
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
