"""
Security middleware for headers, rate limiting, and other security features
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import hashlib
from typing import Dict, Optional
from collections import defaultdict, deque
import asyncio

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60, burst_size: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
            else:
                client_ip = request.client.host if request.client else "unknown"
        
        # Add user agent hash for additional uniqueness
        user_agent = request.headers.get("User-Agent", "")
        user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
        
        return f"{client_ip}:{user_agent_hash}"
    
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove requests older than 1 minute
        while client_requests and client_requests[0] < now - 60:
            client_requests.popleft()
        
        # Check if over limit
        if len(client_requests) >= self.requests_per_minute:
            return True
        
        # Check burst limit (requests in last 10 seconds)
        recent_requests = [req_time for req_time in client_requests if req_time > now - 10]
        if len(recent_requests) >= self.burst_size:
            return True
        
        return False
    
    def record_request(self, client_id: str):
        """Record a request for rate limiting"""
        now = time.time()
        self.requests[client_id].append(now)
    
    def cleanup_old_entries(self):
        """Clean up old rate limiting entries"""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            # Remove clients with no recent requests
            clients_to_remove = []
            for client_id, requests in self.requests.items():
                # Remove old requests
                while requests and requests[0] < now - 60:
                    requests.popleft()
                
                # Mark for removal if no recent requests
                if not requests:
                    clients_to_remove.append(client_id)
            
            for client_id in clients_to_remove:
                del self.requests[client_id]
            
            self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next):
        # Cleanup old entries periodically
        self.cleanup_old_entries()
        
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if self.is_rate_limited(client_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.record_request(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - len(self.requests[client_id]))
        )
        
        return response

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware"""
    
    def __init__(self, app: ASGIApp, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
        self.csrf_tokens: Dict[str, str] = {}
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate a CSRF token for a session"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        return token
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """Verify a CSRF token"""
        expected_token = self.csrf_tokens.get(session_id)
        return expected_token and expected_token == token
    
    def get_session_id(self, request: Request) -> Optional[str]:
        """Get session ID from request"""
        # Try to get from Authorization header (JWT)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For JWT, we could extract user ID as session identifier
            # This is a simplified approach
            return "jwt_session"
        
        # Try to get from session cookie
        session_cookie = request.cookies.get("session_id")
        if session_cookie:
            return session_cookie
        
        return None
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods and auth endpoints
        if (request.method in ["GET", "HEAD", "OPTIONS"] or 
            request.url.path.startswith("/auth/")):
            response = await call_next(request)
            return response
        
        session_id = self.get_session_id(request)
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF protection: No session found"
            )
        
        # Check CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or not self.verify_csrf_token(session_id, csrf_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF protection: Invalid token"
            )
        
        response = await call_next(request)
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log security-relevant requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    def get_client_info(self, request: Request) -> Dict[str, str]:
        """Extract client information for logging"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
            else:
                client_ip = request.client.host if request.client else "unknown"
        
        return {
            "ip": client_ip,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query) if request.url.query else "",
            "referer": request.headers.get("Referer", ""),
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_info = self.get_client_info(request)
        
        # Log suspicious patterns
        suspicious_patterns = [
            "..",  # Path traversal
            "<script",  # XSS attempt
            "union select",  # SQL injection
            "exec(",  # Code injection
            "eval(",  # Code injection
        ]
        
        request_str = f"{request.method} {request.url.path} {request.url.query}".lower()
        is_suspicious = any(pattern in request_str for pattern in suspicious_patterns)
        
        if is_suspicious:
            print(f"🚨 SUSPICIOUS REQUEST: {client_info}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        status_code = response.status_code
        
        # Log failed requests
        if status_code >= 400:
            print(f"❌ FAILED REQUEST: {client_info} -> {status_code} ({duration:.3f}s)")
        elif is_suspicious:
            print(f"⚠️  SUSPICIOUS REQUEST: {client_info} -> {status_code} ({duration:.3f}s)")
        
        return response
