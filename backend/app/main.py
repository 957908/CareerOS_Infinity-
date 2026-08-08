import time
import logging
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_structured_logging
from app.core.exceptions import register_custom_exception_handlers
from app.core.middleware import CorrelationIdMiddleware
from app.core.metrics import router as metrics_router
from app.api.auth import router as auth_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router

from contextlib import asynccontextmanager
from app.core.database import Base, engine
from app.models.user import User
from app.models.resume import Resume
from app.models.graph import EntityNode, RelationshipEdge

# Setup structured logging immediately
setup_structured_logging()
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: Initializing database schema and pgvector extension...")
    try:
        async with engine.begin() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Lifespan: Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Lifespan: Error during database initialization: {e}", exc_info=True)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Bind correlation ID tracer and CORS Middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom API exception handlers
register_custom_exception_handlers(app)

@app.middleware("http")
async def log_execution_time_middleware(request: Request, call_next) -> Response:
    """
    Middleware tracking execution latency for telemetry.
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"HTTP request: method={request.method} path={request.url.path} "
        f"status={response.status_code} duration_ms={duration * 1000:.2f}ms"
    )
    response.headers["X-Response-Time-Ms"] = f"{duration * 1000:.2f}"
    return response

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """
    Central API health checker. Used by docker-compose and Kubernetes probes.
    """
    logger.info("Health check endpoint invoked.")
    return {"status": "healthy", "version": settings.VERSION}

# Register platform api routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)

@app.websocket("/ws/interviews/{session_id}")
async def mock_interview_websocket(websocket: WebSocket, session_id: str):
    """
    Websocket server handler loop for real-time coach interactions.
    """
    await websocket.accept()
    logger.info(f"WebSocket session established for coach loop: {session_id}")
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"WebSocket packet received on session {session_id}: {data}")
            # Mock feedback loop matching protocol schema specs
            response_payload = {
                "event": "coach_feedback",
                "data": {
                    "question": "Excellent response. Can you detail your exact concurrency control?",
                    "feedback_metrics": {
                        "star_structure_check": {"situation": True, "task": True, "action": True, "result": False},
                        "pacing_words_per_minute": 120
                    }
                }
            }
            await websocket.send_json(response_payload)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for coach session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error on session {session_id}: {e}", exc_info=True)
