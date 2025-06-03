from redis.asyncio import Redis
from app.core.config import settings

# Create a Redis client
redis_client = Redis.from_url(settings.REDIS_DSN, decode_responses=True)

async def get_redis() -> Redis:
    """Dependency for getting redis client"""
    try:
        # Check connection
        await redis_client.ping()
        yield redis_client
    finally:
        # Connection will be closed by Redis client when it goes out of scope
        pass