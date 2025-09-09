# Request/response logging
# backend/app/middleware/request_logging.py
import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from uuid import uuid4

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Response]
    ) -> Response:
        # Generate request ID
        request_id = str(uuid4())
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            "HTTP request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "HTTP request completed",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=round(duration, 4),
        )
        
        # Add request ID to response headers (useful for debugging)
        response.headers["X-Request-ID"] = request_id
        
        return response
