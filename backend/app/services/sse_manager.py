import asyncio
import json
from datetime import datetime, timezone
from typing import Any


class SSEManager:
    """Manages Server-Sent Events for live alert streaming."""

    def __init__(self):
        self._queues: list[asyncio.Queue] = []

    async def subscribe(self):
        queue: asyncio.Queue = asyncio.Queue()
        self._queues.append(queue)
        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self._queues.remove(queue)

    async def publish(self, event_type: str, data: dict[str, Any]):
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        payload = json.dumps(message, default=str)
        for queue in self._queues:
            await queue.put(payload)


sse_manager = SSEManager()
