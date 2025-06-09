import os
import logging
from typing import Optional

import redis


logger = logging.getLogger(__name__)


class RedisHandler:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD", None)

        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )

    def is_rate_limited(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        """
        Returns True if the given key (IP, user, etc.) exceeded the max allowed attempts within the time window.
        """
        try:
            current = self.client.get(key)
            if current and int(current) >= max_attempts:
                return True

            pipe = self.client.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, window_seconds)
            pipe.execute()
            return False
        except redis.RedisError as e:
            logger.error("Redis error during rate limiting", exc_info=e)
            return False

    def reset_key(self, key: str):
        """Resets the count for a given key."""
        self.client.delete(key)

    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None):
        self.client.set(key, value, ex=ex)

    def incr(self, key: str):
        self.client.incr(key)

    def delete(self, key: str):
        self.client.delete(key)
    
    def healthcheck(self) -> bool:
        """Check if Redis is available."""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            logger.error("Redis health check failed")
            return False
        except redis.RedisError as e:
            logger.error("Redis error during health check", exc_info=e)
            return False
