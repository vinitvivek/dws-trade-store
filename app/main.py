"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.repositories.postgres_repository import PostgresRepository
from app.repositories.mongodb_repository import MongoDBRepository
from app.services.trade_service import TradeService
from app.services.expiry_scheduler import ExpiryScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global scheduler
    
    # Startup
    logger.info("Starting Trade Store Application...")
    settings = get_settings()
    
    # Initialize database
    postgres_repo = PostgresRepository()
    postgres_repo.create_tables()
    logger.info("Database tables initialized")
    
    # Start expiry scheduler
    mongodb_repo = MongoDBRepository()
    trade_service = TradeService(postgres_repo, mongodb_repo)
    scheduler = ExpiryScheduler(
        trade_service,
        interval_minutes=settings.EXPIRY_CHECK_INTERVAL_MINUTES
    )
    scheduler.start()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.stop()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Trade Store API",
    description="Trade Store with Kafka, PostgreSQL, and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["trades"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Trade Store API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )