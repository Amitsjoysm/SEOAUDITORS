"""Rate limiting middleware for production scalability"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter for API endpoints (Redis-ready for production)"""
    
    def __init__(self):
        # Store: {ip: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
        
        # Rate limits (requests per minute)
        self.limits = {
            "default": 60,  # 60 requests per minute
            "audit_create": 5,  # Only 5 audit creations per minute
            "chat": 30,  # 30 chat messages per minute
            "report": 10,  # 10 report downloads per minute
        }
        
        # Time window (seconds)
        self.window = 60
    
    async def cleanup_old_requests(self, ip: str):
        """Remove requests older than the time window"""
        current_time = time.time()
        async with self.lock:
            self.requests[ip] = [
                (ts, endpoint) for ts, endpoint in self.requests[ip]
                if current_time - ts < self.window
            ]
    
    async def check_rate_limit(self, ip: str, endpoint: str = "default") -> Tuple[bool, int]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, remaining_requests)
        """
        await self.cleanup_old_requests(ip)
        
        current_time = time.time()
        limit = self.limits.get(endpoint, self.limits["default"])
        
        async with self.lock:
            # Count requests for this endpoint
            endpoint_requests = [
                ts for ts, ep in self.requests[ip]
                if ep == endpoint or endpoint == "default"
            ]
            
            request_count = len(endpoint_requests)
            
            if request_count >= limit:
                # Rate limit exceeded
                oldest_request = min(endpoint_requests)
                reset_time = int(oldest_request + self.window - current_time)
                return False, 0
            
            # Add new request
            self.requests[ip].append((current_time, endpoint))
            remaining = limit - request_count - 1
            
            return True, remaining
    
    async def get_rate_limit_info(self, ip: str, endpoint: str = "default") -> Dict:
        """Get rate limit information for an IP"""
        await self.cleanup_old_requests(ip)
        
        limit = self.limits.get(endpoint, self.limits["default"])
        
        async with self.lock:
            endpoint_requests = [
                ts for ts, ep in self.requests[ip]
                if ep == endpoint or endpoint == "default"
            ]
            
            request_count = len(endpoint_requests)
            remaining = max(0, limit - request_count)
            
            if endpoint_requests:
                oldest_request = min(endpoint_requests)
                reset_time = int(oldest_request + self.window - time.time())
            else:
                reset_time = self.window
            
            return {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "window": self.window
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, endpoint: str = "default"):
    """Middleware function to check rate limits"""
    # Get client IP
    client_ip = request.client.host
    
    # Check forwarded headers for real IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    # Check rate limit
    is_allowed, remaining = await rate_limiter.check_rate_limit(client_ip, endpoint)
    
    if not is_allowed:
        # Get rate limit info for error message
        info = await rate_limiter.get_rate_limit_info(client_ip, endpoint)
        logger.warning(f"Rate limit exceeded for {client_ip} on endpoint {endpoint}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {info['reset']} seconds.",
            headers={
                "X-RateLimit-Limit": str(info['limit']),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info['reset']),
                "Retry-After": str(info['reset'])
            }
        )
    
    # Add rate limit headers to response
    info = await rate_limiter.get_rate_limit_info(client_ip, endpoint)
    
    # Store in request state for adding to response
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(info['limit']),
        "X-RateLimit-Remaining": str(info['remaining']),
        "X-RateLimit-Reset": str(info['reset'])
    }
    
    return True


# Decorator for easy use
def rate_limit(endpoint: str = "default"):
    """Decorator to apply rate limiting to a route"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            await rate_limit_middleware(request, endpoint)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
