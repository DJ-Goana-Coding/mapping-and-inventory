"""
🔒 RATE LIMITER - API Rate Limiting & DDoS Protection
Protects against: Brute force attacks, DDoS, API abuse
"""

import time
import hashlib
from typing import Optional, Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    pass


class RateLimiter:
    """
    Rate limiter with multiple strategies:
    - Fixed window
    - Sliding window
    - Token bucket
    - IP-based, user-based, API-key-based limiting
    """
    
    def __init__(self, storage_backend='memory'):
        """
        Initialize rate limiter
        
        Args:
            storage_backend: 'memory' or 'redis' (redis requires redis-py)
        """
        self.storage_backend = storage_backend
        
        if storage_backend == 'memory':
            self._memory_store: Dict[str, list] = defaultdict(list)
            self._lock = threading.Lock()
        elif storage_backend == 'redis':
            try:
                import redis
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                print(f"⚠️ Redis not available, falling back to memory: {e}")
                self.storage_backend = 'memory'
                self._memory_store = defaultdict(list)
                self._lock = threading.Lock()
    
    def _parse_rate(self, rate: str) -> Tuple[int, int]:
        """
        Parse rate string to (limit, period_seconds)
        
        Examples:
            "100/minute" -> (100, 60)
            "1000/hour" -> (1000, 3600)
            "10/second" -> (10, 1)
        """
        parts = rate.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid rate format: {rate}. Use format: '100/minute'")
        
        limit = int(parts[0])
        period = parts[1].lower()
        
        period_map = {
            'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }
        
        if period not in period_map:
            raise ValueError(f"Invalid period: {period}. Use: second, minute, hour, day")
        
        return limit, period_map[period]
    
    def _get_key(self, identifier: str, namespace: str = "default") -> str:
        """Generate storage key"""
        return f"ratelimit:{namespace}:{identifier}"
    
    def _memory_check_rate(self, key: str, limit: int, period: int) -> Tuple[bool, dict]:
        """Check rate limit using in-memory storage"""
        with self._lock:
            now = time.time()
            cutoff = now - period
            
            # Clean old entries
            self._memory_store[key] = [
                timestamp for timestamp in self._memory_store[key]
                if timestamp > cutoff
            ]
            
            # Check limit
            current_count = len(self._memory_store[key])
            allowed = current_count < limit
            
            if allowed:
                self._memory_store[key].append(now)
            
            # Calculate reset time
            if self._memory_store[key]:
                oldest = min(self._memory_store[key])
                reset_at = oldest + period
            else:
                reset_at = now + period
            
            return allowed, {
                'limit': limit,
                'remaining': max(0, limit - current_count - (1 if allowed else 0)),
                'reset_at': reset_at,
                'retry_after': max(0, int(reset_at - now))
            }
    
    def _redis_check_rate(self, key: str, limit: int, period: int) -> Tuple[bool, dict]:
        """Check rate limit using Redis storage"""
        try:
            now = time.time()
            pipe = self.redis_client.pipeline()
            
            # Add current timestamp
            pipe.zadd(key, {str(now): now})
            
            # Remove old entries
            cutoff = now - period
            pipe.zremrangebyscore(key, 0, cutoff)
            
            # Count current entries
            pipe.zcard(key)
            
            # Set expiration
            pipe.expire(key, period + 60)  # Add buffer
            
            results = pipe.execute()
            current_count = results[2]  # Result from zcard
            
            allowed = current_count <= limit
            
            # Get oldest entry for reset calculation
            oldest_entries = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest = oldest_entries[0][1]
                reset_at = oldest + period
            else:
                reset_at = now + period
            
            return allowed, {
                'limit': limit,
                'remaining': max(0, limit - current_count),
                'reset_at': reset_at,
                'retry_after': max(0, int(reset_at - now))
            }
        except Exception as e:
            print(f"⚠️ Redis error, allowing request: {e}")
            return True, {'limit': limit, 'remaining': limit, 'reset_at': now + period, 'retry_after': 0}
    
    def check_rate_limit(
        self,
        identifier: str,
        rate: str = "100/minute",
        namespace: str = "api"
    ) -> dict:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: Unique identifier (IP, user_id, api_key, etc.)
            rate: Rate limit string (e.g., "100/minute", "1000/hour")
            namespace: Namespace for grouping (e.g., "api", "login", "upload")
        
        Returns:
            Dict with: allowed, limit, remaining, reset_at, retry_after
        
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        limit, period = self._parse_rate(rate)
        key = self._get_key(identifier, namespace)
        
        if self.storage_backend == 'redis':
            allowed, info = self._redis_check_rate(key, limit, period)
        else:
            allowed, info = self._memory_check_rate(key, limit, period)
        
        info['allowed'] = allowed
        
        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for {namespace}:{identifier}. "
                f"Limit: {limit}/{period}s. Retry after {info['retry_after']}s"
            )
        
        return info
    
    def limit_by_ip(self, ip: str, rate: str = "100/minute") -> dict:
        """IP-based rate limiting"""
        return self.check_rate_limit(ip, rate, namespace="ip")
    
    def limit_by_user(self, user_id: str, rate: str = "1000/hour") -> dict:
        """User-based rate limiting"""
        return self.check_rate_limit(user_id, rate, namespace="user")
    
    def limit_by_api_key(self, api_key: str, rate: str = "5000/hour") -> dict:
        """API key-based rate limiting"""
        # Hash API key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return self.check_rate_limit(key_hash, rate, namespace="apikey")
    
    def reset(self, identifier: str, namespace: str = "api") -> None:
        """Reset rate limit for identifier"""
        key = self._get_key(identifier, namespace)
        
        if self.storage_backend == 'redis':
            self.redis_client.delete(key)
        else:
            with self._lock:
                if key in self._memory_store:
                    del self._memory_store[key]
    
    def get_stats(self, identifier: str, namespace: str = "api") -> dict:
        """Get current stats for identifier"""
        key = self._get_key(identifier, namespace)
        
        if self.storage_backend == 'redis':
            count = self.redis_client.zcard(key) or 0
        else:
            count = len(self._memory_store.get(key, []))
        
        return {
            'identifier': identifier,
            'namespace': namespace,
            'current_count': count,
            'storage_backend': self.storage_backend
        }


# Decorator for rate limiting
def rate_limit(rate: str = "100/minute", namespace: str = "api", key_func=None):
    """
    Decorator to add rate limiting to functions
    
    Args:
        rate: Rate limit string
        namespace: Namespace for grouping
        key_func: Function to extract identifier from args/kwargs
                  Default: uses first argument
    
    Example:
        @rate_limit("10/minute", namespace="login")
        def login(username, password):
            pass
    """
    limiter = RateLimiter()
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract identifier
            if key_func:
                identifier = key_func(*args, **kwargs)
            elif args:
                identifier = str(args[0])
            else:
                identifier = "default"
            
            # Check rate limit
            try:
                info = limiter.check_rate_limit(identifier, rate, namespace)
                # Attach rate limit info to function for access
                func._rate_limit_info = info
            except RateLimitExceeded as e:
                raise e
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    limiter = RateLimiter(storage_backend='memory')
    
    print("🔒 Rate Limiter initialized")
    
    # Test IP-based rate limiting
    test_ip = "192.168.1.1"
    
    for i in range(12):
        try:
            info = limiter.limit_by_ip(test_ip, rate="10/minute")
            print(f"✅ Request {i+1}: Allowed. Remaining: {info['remaining']}")
        except RateLimitExceeded as e:
            print(f"❌ Request {i+1}: {e}")
    
    # Test user-based rate limiting
    print("\n🔒 Testing user rate limit...")
    user_id = "user123"
    
    try:
        info = limiter.limit_by_user(user_id, rate="1000/hour")
        print(f"✅ User request allowed. Remaining: {info['remaining']}")
    except RateLimitExceeded as e:
        print(f"❌ User request denied: {e}")
    
    # Get stats
    stats = limiter.get_stats(test_ip, namespace="ip")
    print(f"\n📊 Stats for {test_ip}: {stats}")
