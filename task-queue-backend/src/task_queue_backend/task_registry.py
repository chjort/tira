"""Redis-based task registry for persisting submitted research tasks.

Stores task metadata (task_id, theme, submitted_at) in a Redis sorted set
so that the frontend can recover the task list after a page refresh.
"""

import json
import time
from datetime import UTC, datetime

import redis

REGISTRY_KEY = "tira:tasks"


def get_redis_client(url: str) -> redis.Redis:
    """Create a Redis client from a URL.

    Args:
        url: Redis connection URL (e.g. ``redis://localhost:6379/0``).

    Returns:
        A ``redis.Redis`` instance with decoded string responses.
    """
    return redis.Redis.from_url(url, decode_responses=True)


def register_task(client: redis.Redis, task_id: str, theme: str) -> None:
    """Register a newly submitted task in the registry.

    Args:
        client: Redis client.
        task_id: Celery task ID (UUID string).
        theme: The investment theme submitted by the user.
    """
    entry = json.dumps(
        {
            "task_id": task_id,
            "theme": theme,
            "submitted_at": datetime.now(UTC).isoformat(),
        }
    )
    client.zadd(REGISTRY_KEY, {entry: time.time()})


def list_tasks(client: redis.Redis) -> list[dict]:
    """Return all registered tasks ordered by submission time (oldest first).

    Args:
        client: Redis client.

    Returns:
        List of dicts with ``task_id``, ``theme``, and ``submitted_at`` keys.
    """
    members = client.zrange(REGISTRY_KEY, 0, -1)
    return [json.loads(m) for m in members]
