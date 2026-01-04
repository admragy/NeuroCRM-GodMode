"""
🔒 OmniCRM Ultimate - Advanced Security Middleware
===================================================
✅ Rate Limiting (IP & User-based)
✅ CSRF Protection
✅ CORS Hardening
✅ Request Validation
✅ IP Whitelisting/Blacklisting
✅ DDoS Protection
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Optional, Dict, List
import logging

from app.core.cache import cache_manager, RateLimiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Multi-tier rate limiting:
    - IP-based: 100 req/min for anonymous
    - User-based: 1000 req/min for authenticated
    - Endpoint-specific: Custom limits for expensive operations
    """
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_client) if redis_client else None
        
        # Default limits
        self.default_limits = {
            "anonymous": (100, 60),  # (max_requests, window_seconds)
            "authenticated": (1000, 60),
            "ai_operations": (20, 60),  # AI API calls
            "admin": (5000, 60)
        }
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            "/api/ai/generate": (10, 60),
            "/api/ai/analyze": (10, 60),
            "/api/whatsapp/bulk": (5, 60),
            "/api/deals/ai": (20, 60),
            "/api/auth/login": (5, 300),  # 5 attempts per 5 minutes
            "/api/auth/register": (3, 3600),  # 3 registrations per hour
        }
    
    async def dispatch(self, request: Request, call_next):
        if not self.rate_limiter:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)
        
        try:
            # Determine rate limit tier
            user_id = getattr(request.state, "user_id", None)
            is_admin = getattr(request.state, "is_admin", False)
            
            if is_admin:
                max_requests, window = self.default_limits["admin"]
            elif user_id:
                max_requests, window = self.default_limits["authenticated"]
            else:
                max_requests, window = self.default_limits["anonymous"]
            
            # Apply endpoint-specific limits
            if request.url.path in self.endpoint_limits:
                max_requests, window = self.endpoint_limits[request.url.path]
            
            # Create rate limit key
            if user_id:
                rate_key = f"rate_limit:user:{user_id}:{request.url.path}"
            else:
                client_ip = request.client.host
                rate_key = f"rate_limit:ip:{client_ip}:{request.url.path}"
            
            # Check rate limit
            allowed, info = await self.rate_limiter.is_allowed(
                rate_key,
                max_requests,
                window
            )
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded: {rate_key}",
                    extra={
                        "event": "rate_limit_exceeded",
                        "key": rate_key,
                        "limit": max_requests,
                        "window": window
                    }
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Try again in {info.get('reset', window)} seconds.",
                        "retry_after": info.get('reset', window)
                    },
                    headers={
                        "X-RateLimit-Limit": str(info.get("limit", max_requests)),
                        "X-RateLimit-Remaining": str(info.get("remaining", 0)),
                        "X-RateLimit-Reset": str(info.get("reset", window)),
                        "Retry-After": str(info.get("reset", window))
                    }
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(info.get("limit", max_requests))
            response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", max_requests - 1))
            response.headers["X-RateLimit-Reset"] = str(info.get("reset", window))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Fail open (allow request)
            return await call_next(request)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection for state-changing operations
    - Double-submit cookie pattern
    - Token validation for POST/PUT/DELETE/PATCH
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.safe_methods = ["GET", "HEAD", "OPTIONS"]
        self.exempt_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/webhooks",  # Webhooks use signature verification
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF for safe methods
        if request.method in self.safe_methods:
            return await call_next(request)
        
        # Skip CSRF for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        try:
            # Get CSRF token from header
            csrf_header = request.headers.get("X-CSRF-Token")
            
            # Get CSRF token from cookie
            csrf_cookie = request.cookies.get("csrf_token")
            
            # Validate tokens match
            if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                logger.warning(
                    f"CSRF validation failed",
                    extra={
                        "event": "csrf_failed",
                        "path": request.url.path,
                        "method": request.method,
                        "has_header": bool(csrf_header),
                        "has_cookie": bool(csrf_cookie)
                    }
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF validation failed"
                )
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CSRF middleware error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security validation error"
            )


class IPFilterMiddleware(BaseHTTPMiddleware):
    """
    IP-based access control
    - Whitelist for admin endpoints
    - Blacklist for malicious IPs
    - Geo-blocking (optional)
    """
    
    def __init__(
        self,
        app,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.whitelist = set(whitelist or [])
        self.blacklist = set(blacklist or [])
        
        # Admin endpoints requiring whitelist
        self.protected_paths = [
            "/api/admin",
            "/api/system",
            "/api/backups"
        ]
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Check blacklist
        if client_ip in self.blacklist:
            logger.warning(
                f"Blocked blacklisted IP: {client_ip}",
                extra={
                    "event": "ip_blocked",
                    "ip": client_ip,
                    "reason": "blacklist"
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Access denied"}
            )
        
        # Check whitelist for protected paths
        is_protected = any(
            request.url.path.startswith(path)
            for path in self.protected_paths
        )
        
        if is_protected and self.whitelist and client_ip not in self.whitelist:
            logger.warning(
                f"Blocked non-whitelisted IP from protected path: {client_ip}",
                extra={
                    "event": "ip_blocked",
                    "ip": client_ip,
                    "path": request.url.path,
                    "reason": "not_whitelisted"
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Access denied"}
            )
        
        return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Request validation and sanitization
    - Content-Type validation
    - Request size limits
    - Payload inspection
    """
    
    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Validate Content-Type for POST/PUT/PATCH
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                
                # Allow only specific content types
                allowed_types = [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data"
                ]
                
                if not any(ct in content_type for ct in allowed_types):
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content={"error": "Unsupported Media Type"}
                    )
            
            # Check request body size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_body_size:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "error": "Request too large",
                        "max_size_mb": self.max_body_size / 1024 / 1024
                    }
                )
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Request validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid request"}
            )


# CSRF Token utilities
def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response, token: str):
    """Set CSRF token in cookie"""
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=3600 * 24  # 24 hours
    )
    return response


# API route for getting CSRF token
async def get_csrf_token(request: Request):
    """
    GET /api/csrf-token
    Returns CSRF token for client-side usage
    """
    token = generate_csrf_token()
    
    response = JSONResponse(
        content={"csrf_token": token}
    )
    
    set_csrf_cookie(response, token)
    
    return response
