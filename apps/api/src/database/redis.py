"""Redis Async Client Pool for Caching and Pub/Sub."""

import os
from typing import Any


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_redis_client() -> dict[str, Any]:
    """Redis connection configuration skeleton."""
    return {
        "url": get_redis_url(),
        "default_ttl_seconds": 3600,
    }
