import json

import redis
from redis.asyncio import Redis as AsyncRedis

from src.common.config import get_settings

settings = get_settings()
CHANNEL_NAME = "rag_events"


def publish_event_sync(payload: dict) -> None:
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        client.publish(CHANNEL_NAME, json.dumps(payload))
    finally:
        client.close()


async def subscribe_events():
    client = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)
    try:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            data = message.get("data")
            if isinstance(data, str):
                yield json.loads(data)
    finally:
        await pubsub.unsubscribe(CHANNEL_NAME)
        await pubsub.close()
        await client.close()
