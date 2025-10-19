"""
FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.core.config import settings
from app.core.logger import setup_logging
from app.data.models import HealthCheckResponse, SystemInfoResponse
from app.data.database import check_db_connection
from app.data.vector_index import initialize_vector_index
from app.core.monitoring import initialize_monitoring
from app.routes import benefit_verification, policy_search, clinical_qualification, prior_authorization, orchestrator, monitoring_demo

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown"""
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Develop Health MVP API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"OpenRouter Model: {settings.openrouter_model}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info("=" * 50)
    
    # Create necessary directories
    Path(settings.pa_forms_output_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.mock_data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
    
    # Check database connection
    logger.info("Checking database connection...")
    db_status = check_db_connection()
    if db_status:
        logger.info("✓ Database connection successful")
    else:
        logger.warning("⚠ Database connection failed - some features may not work")
        logger.warning("  Run 'docker-compose up -d' to start PostgreSQL")
    
    # Initialize vector index
    logger.info("Initializing ChromaDB vector index...")
    try:
        vector_manager = initialize_vector_index()
        stats = vector_manager.get_collection_stats()
        logger.info(f"✓ ChromaDB initialized with {stats['document_count']} documents")
        if stats['document_count'] == 0:
            logger.warning("⚠ Vector index is empty - run 'python scripts/build_vector_index.py'")
    except Exception as e:
        logger.warning(f"⚠ ChromaDB initialization warning: {e}")
    
    # Initialize monitoring
    logger.info("Initializing monitoring...")
    try:
        initialize_monitoring()
        logger.info("✓ Monitoring initialized")
    except Exception as e:
        logger.warning(f"⚠ Monitoring initialization warning: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Develop Health MVP API...")


# Create FastAPI app
app = FastAPI(
    title="Develop Health MVP - AI Prior Authorization",
    description="AI-powered healthcare automation for benefit verification, clinical qualification, and prior authorization",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(benefit_verification.router)
app.include_router(policy_search.router)
app.include_router(clinical_qualification.router)
app.include_router(prior_authorization.router)
app.include_router(orchestrator.router)
app.include_router(monitoring_demo.router)


# ==================== Root Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Develop Health MVP - AI Prior Authorization API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "info": "/info",
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns service status and basic information
    """
    return HealthCheckResponse(
        status="healthy",
        service="develop-health-mvp",
        version="1.0.0"
    )


@app.get("/info", response_model=SystemInfoResponse, tags=["Health"])
async def system_info():
    """
    System information endpoint
    
    Returns current configuration and service status
    """
    # Check database connection
    database_connected = check_db_connection()
    
    # TODO: Add Redis connection check in Phase 6
    redis_connected = False
    
    # ChromaDB will be initialized in Phase 3
    chromadb_initialized = False
    
    return SystemInfoResponse(
        environment=settings.environment,
        openrouter_model=settings.openrouter_model,
        database_connected=database_connected,
        redis_connected=redis_connected,
        chromadb_initialized=chromadb_initialized,
    )


# ==================== Phase-specific routes will be added here ====================
# Phase 2: Benefit Verification routes
# Phase 3: ChromaDB search routes
# Phase 4: Clinical Qualification routes
# Phase 5: Prior Authorization routes
# Phase 6: Orchestrator routes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

