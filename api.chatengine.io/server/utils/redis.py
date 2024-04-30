import redis
from server.settings.base import REDIS_HOST, REDIS_PORT

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            decode_responses=True # Decode to utf-8
        )

    def publish_message(self, channel: str, message: object):
        self.client.publish(channel, message)
