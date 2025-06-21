"""
Rate limiting middleware for DoR-Dash API endpoints.
Implements sliding window rate limiting to prevent abuse.
"""
import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limit."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests outside the window
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
            
            # Check if we're within the limit
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, rate_limiters: Dict[str, SlidingWindowRateLimiter]):
        super().__init__(app)
        self.rate_limiters = rate_limiters
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP for rate limiting
        client_ip = self._get_client_ip(request)
        
        # Apply rate limiting based on endpoint
        path = request.url.path
        
        # Authentication endpoints - strict rate limiting
        if path.startswith('/api/v1/auth/login'):
            limiter = self.rate_limiters.get('auth_login')
            if limiter and not await limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many login attempts. Please try again later."
                )
        
        # Registration endpoints - moderate rate limiting
        elif path.startswith('/api/v1/auth/register'):
            limiter = self.rate_limiters.get('auth_register')
            if limiter and not await limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many registration attempts. Please try again later."
                )
        
        # General API endpoints - relaxed rate limiting
        elif path.startswith('/api/v1/'):
            limiter = self.rate_limiters.get('api_general')
            if limiter and not await limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please slow down."
                )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling reverse proxy headers."""
        # Check for real IP from reverse proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return request.client.host if request.client else "unknown"

# Pre-configured rate limiters
def create_rate_limiters() -> Dict[str, SlidingWindowRateLimiter]:
    """Create and configure rate limiters for different endpoint categories."""
    return {
        # Login attempts: 5 attempts per minute
        'auth_login': SlidingWindowRateLimiter(max_requests=5, window_seconds=60),
        
        # Registration attempts: 3 attempts per hour
        'auth_register': SlidingWindowRateLimiter(max_requests=3, window_seconds=3600),
        
        # General API calls: 100 requests per minute
        'api_general': SlidingWindowRateLimiter(max_requests=100, window_seconds=60),
    }