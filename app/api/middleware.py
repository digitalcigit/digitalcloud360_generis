"""Custom middleware for Genesis AI Service"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog
from prometheus_client import Counter, Histogram, generate_latest

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('genesis_ai_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('genesis_ai_request_duration_seconds', 'Request duration', ['method', 'endpoint'])

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration_seconds=duration
        )
        
        return response

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics collection"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract endpoint for metrics
        endpoint = request.url.path
        method = request.method
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
