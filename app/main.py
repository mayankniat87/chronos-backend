import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.models.restaurant import Restaurant
from app.api import routes_upload, routes_graph, routes_decision, routes_health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Database bootstrap -----------------------------------------------------
# For a hackathon demo we still want create_all() to run at startup, but a
# silent failure here means every request will 500 later with a confusing
# "no such table" error. Fail fast and loud instead so the problem is caught
# during boot, not mid-demo.
logger.info("Initializing database tables...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception:
    logger.critical("Database initialization failed. The app cannot serve requests.", exc_info=True)
    raise

# --- App setup ---------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Explainable Business Time Machine backend API for hackathons.",
)

# CORS: allow_credentials=True is only valid with an explicit origin list.
# Browsers reject the wildcard-origin + credentials=True combination outright,
# which silently breaks any frontend using fetch(..., {credentials: "include"}).
_origins = settings.cors_origin_list
_allow_credentials = _origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    """Attaches a request id for log correlation and logs request timing.
    This is the minimum viable observability layer for a demo: without it,
    a slow/failing request during judging is impossible to trace after the fact.
    """
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} failed after {duration_ms:.1f}ms",
            exc_info=True,
        )
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Last-resort safety net. Without this, an uncaught exception anywhere
    (e.g. a pydantic ValidationError raised by response_model validation,
    which is NOT caught by the per-route try/except blocks) surfaces as a
    bare 500 with no JSON body, which breaks the frontend's error handling
    mid-demo.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# --- Routers -----------------------------------------------------------------
app.include_router(routes_upload.router)
app.include_router(routes_graph.router)
app.include_router(routes_decision.router)
app.include_router(routes_health.router)


@app.get("/healthz", tags=["infra"], summary="Liveness probe")
def healthz():
    """Plain infra liveness check, separate from /health/{restaurant_id}
    (which is a business metric, not a service health probe -- see the
    naming-collision note in routes_health.py)."""
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "Chronos Backend",
        "description": "Decision Intelligence platform for SMEs.",
        "documentation": "/docs",
    }
