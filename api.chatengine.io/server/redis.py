import redis
from server import settings

# Create a Redis pubsub connection
redis_pubsub = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=1
)

# Create a Redis cache connection
redis_cache = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=0
)
