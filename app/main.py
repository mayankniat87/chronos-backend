import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import engine, Base, and Models to ensure SQLAlchemy loads metadata before startup table creation
from app.core.database import engine, Base
from app.models.restaurant import Restaurant  # registers all models implicitly in metadata

# Import routers
from app.api import routes_upload, routes_graph, routes_decision, routes_health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chronos_backend")

# Initialize FastAPI application
app = FastAPI(
    title="Project Chronos - Explainable Business Time Machine API",
    description="Backend Core Engine and Onboarding Pipelines for SME Restaurant Simulations",
    version="1.0.0"
)

# Configure CORS for Next.js frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon ease; restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB Schema Creation
@app.on_event("startup")
def startup_event():
    logger.info("Initializing database schemas...")
    try:
        # Automatically creates SQLite/Postgres tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.error(f"Error during schema initialization: {e}")

# Register Routers
app.include_router(routes_upload.router)
app.include_router(routes_graph.router)
app.include_router(routes_decision.router)
app.include_router(routes_health.router)

@app.get("/")
def read_root():
    return {
        "project": "Project Chronos",
        "description": "Explainable Business Time Machine Backend API",
        "status": "online",
        "documentation": "/docs"
    }
