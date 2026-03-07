"""
Rate Limiter Middleware
"""
from fastapi import Request, HTTPException
from typing import Optional
import time
import hashlib


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.buckets: dict[str, dict] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get from forwarded header (for proxied requests)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fall back to client host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def check_rate_limit(self, request: Request) -> None:
        """Check if request is within rate limit"""
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Initialize bucket if not exists
        if client_id not in self.buckets:
            self.buckets[client_id] = {
                "tokens": self.requests_per_minute,
                "last_update": current_time,
            }
        
        bucket = self.buckets[client_id]
        
        # Calculate token refill
        time_passed = current_time - bucket["last_update"]
        tokens_to_add = (time_passed / 60) * self.requests_per_minute
        bucket["tokens"] = min(
            self.requests_per_minute,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_update"] = current_time
        
        # Check if request can be processed
        if bucket["tokens"] < 1:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Consume token
        bucket["tokens"] -= 1
        
        # Clean up old buckets
        self._cleanup_buckets(current_time)
    
    def _cleanup_buckets(self, current_time: float) -> None:
        """Remove stale buckets"""
        stale_keys = [
            key for key, bucket in self.buckets.items()
            if current_time - bucket["last_update"] > 300  # 5 minutes
        ]
        for key in stale_keys:
            del self.buckets[key]
