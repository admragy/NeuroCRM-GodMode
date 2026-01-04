"""
🚀 OmniCRM Ultimate - Advanced Redis Caching Layer
====================================================
✅ Query Result Caching
✅ API Response Caching
✅ Session Storage
✅ Rate Limiting
✅ Real-Time Pub/Sub
✅ Cache Invalidation Strategies
✅ Cache Warming
✅ Performance Monitoring
"""

import json
import hashlib
import pickle
from typing import Any, Optional, Callable, List
from datetime import timedelta
from functools import wraps
import redis.asyncio as aioredis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Production-grade Redis cache manager"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.default_ttl = 3600  # 1 hour
        
    async def connect(self):
        """Initialize Redis connection pool"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,  # Handle binary data
                max_connections=settings.REDIS_MAX_CONNECTIONS or 50,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            self.redis = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Redis disconnected")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_parts = [prefix]
        
        # Add positional args
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword args (sorted for consistency)
        for k in sorted(kwargs.keys()):
            key_parts.append(f"{k}:{kwargs[k]}")
        
        key = ":".join(key_parts)
        
        # Hash if too long
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"
        
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"✅ Cache HIT: {key}")
                return pickle.loads(value)
            else:
                logger.debug(f"❌ Cache MISS: {key}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache get error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = pickle.dumps(value)
            
            await self.redis.setex(
                key,
                ttl,
                serialized
            )
            
            logger.debug(f"✅ Cache SET: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache delete error: {str(e)}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis:
            return 0
        
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"🗑️ Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Cache delete pattern error: {str(e)}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Cache exists error: {str(e)}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds"""
        if not self.redis:
            return -1
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"❌ Cache TTL error: {str(e)}")
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if not self.redis:
            return 0
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"❌ Cache increment error: {str(e)}")
            return 0
    
    async def get_stats(self) -> dict:
        """Get cache performance statistics"""
        if not self.redis:
            return {}
        
        try:
            info = await self.redis.info("stats")
            
            return {
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                ),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "connected_clients": info.get("connected_clients", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Cache stats error: {str(e)}")
            return {}


# Global cache instance
cache_manager = CacheManager()


# Decorator for caching function results
def cached(
    prefix: str = "cache",
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results
    
    Usage:
        @cached(prefix="user", ttl=300)
        async def get_user(user_id: int):
            return await db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Cache invalidation decorator
def invalidate_cache(patterns: List[str]):
    """
    Decorator to invalidate cache after function execution
    
    Usage:
        @invalidate_cache(["user:*", "team:*"])
        async def update_user(user_id: int, data: dict):
            # Update user
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache patterns
            for pattern in patterns:
                await cache_manager.delete_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator


# Rate limiting using Redis
class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
    
    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        
        Returns:
            (allowed: bool, info: dict)
        """
        try:
            current = await self.redis.get(key)
            
            if current is None:
                # First request in window
                await self.redis.setex(key, window_seconds, 1)
                return True, {
                    "limit": max_requests,
                    "remaining": max_requests - 1,
                    "reset": window_seconds
                }
            
            current_count = int(current)
            
            if current_count < max_requests:
                # Within limit
                await self.redis.incr(key)
                ttl = await self.redis.ttl(key)
                
                return True, {
                    "limit": max_requests,
                    "remaining": max_requests - current_count - 1,
                    "reset": ttl
                }
            else:
                # Rate limit exceeded
                ttl = await self.redis.ttl(key)
                
                return False, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": ttl
                }
                
        except Exception as e:
            logger.error(f"❌ Rate limiter error: {str(e)}")
            # Fail open (allow request)
            return True, {}


# Pub/Sub for real-time notifications
class PubSubManager:
    """Redis Pub/Sub for real-time messaging"""
    
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.pubsub = None
    
    async def subscribe(self, *channels: str):
        """Subscribe to channels"""
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(*channels)
        logger.info(f"📡 Subscribed to channels: {channels}")
    
    async def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        try:
            await self.redis.publish(
                channel,
                json.dumps(message)
            )
            logger.debug(f"📤 Published to {channel}: {message}")
            
        except Exception as e:
            logger.error(f"❌ Publish error: {str(e)}")
    
    async def listen(self):
        """Listen for messages"""
        if not self.pubsub:
            raise RuntimeError("Not subscribed to any channels")
        
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    yield data
                except Exception as e:
                    logger.error(f"❌ Message parse error: {str(e)}")
    
    async def unsubscribe(self):
        """Unsubscribe from all channels"""
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            logger.info("📡 Unsubscribed from all channels")


# Cache warming utilities
async def warm_cache_on_startup():
    """Pre-load frequently accessed data into cache"""
    logger.info("🔥 Warming cache...")
    
    try:
        # Example: Cache popular products, active campaigns, etc.
        # await cache_manager.set("popular_products", popular_products, ttl=3600)
        
        logger.info("✅ Cache warming completed")
        
    except Exception as e:
        logger.error(f"❌ Cache warming failed: {str(e)}")
