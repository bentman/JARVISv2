from __future__ import annotations
import json
import time
import hashlib
from typing import Optional, Any

import redis
from app.core.config import settings


class CacheService:
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.REDIS_URL
        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self) -> None:
        self.client = redis.Redis.from_url(self.url, decode_responses=True)
        # Ping to ensure connection is alive
        self.client.ping()

    def healthy(self) -> bool:
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def key_for_chat(self, mode: str, message: str) -> str:
        h = hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]
        return f"chat:{mode}:{h}"

    def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        payload = json.dumps(value)
        self.client.setex(name=key, time=ttl_seconds, value=payload)

    def get_json(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if not data:
            return None
        return json.loads(data)


cache_service = CacheService()
