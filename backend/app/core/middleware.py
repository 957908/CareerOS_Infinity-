import uuid
import contextvars
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Global contextvar storing active Correlation ID for thread-local logs access
correlation_id_ctx = contextvars.ContextVar("correlation_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware tracing requests via custom X-Correlation-ID headers.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check header values, generate UUID if none exist
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Set token in thread context
        token = correlation_id_ctx.set(corr_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            correlation_id_ctx.reset(token)

def get_current_correlation_id() -> str:
    """
    Utility fetching active correlation ID for logging formatter binding.
    """
    return correlation_id_ctx.get()
