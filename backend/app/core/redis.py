import os
import redis
from app.core.config import settings
from app.core.logger import app_logger

class RedisClient:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", settings.REDIS_URL)
        self.client = None

    def connect(self):
        try:
            self.client = redis.from_url(self.url, decode_responses=True)
            self.client.ping()
            app_logger.info(f"Connected to Redis at {self.url}")
            return self.client
        except Exception as e:
            app_logger.warning(f"Could not connect to Redis at {self.url}: {e}. Running in memory fallback mode.")
            self.client = None
            return None

    def get(self, key: str):
        if self.client:
            try:
                return self.client.get(key)
            except Exception:
                return None
        return None

    def set(self, key: str, value: str, ex: int = None):
        if self.client:
            try:
                return self.client.set(key, value, ex=ex)
            except Exception:
                return False
        return False

redis_client = RedisClient()
