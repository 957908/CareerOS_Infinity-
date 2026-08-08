from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger("app.core.metrics")
router = APIRouter(tags=["Metrics"])

# Define Prometheus metrics variables
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP Requests Count",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency Durations",
    ["method", "endpoint"]
)

WEBSOCKET_CONNECTIONS_ACTIVE = Gauge(
    "websocket_connections_active",
    "Number of active WebSocket sessions"
)

@router.get("/metrics")
def get_metrics() -> Response:
    """
    Exposes raw Prometheus metrics scraped by central logging instances.
    """
    logger.info("Metrics scraping invoked.")
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
