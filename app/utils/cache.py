import json
import redis
from app.config import settings

_redis_client = None



def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client



def cache_get(key: str):
    """Return parsed JSON value or None if key doesn't exist."""
    client = get_redis()
    value = client.get(key)
    if value is None:
        return None
    return json.loads(value)


def cache_set(key: str, value, ttl_seconds: int = 300) -> None:
    """Store value as JSON with a TTL (default 5 min)."""
    client = get_redis()
    client.setex(key, ttl_seconds, json.dumps(value))


def cache_delete(key: str) -> None:
    """Invalidate a cached key."""
    get_redis().delete(key)