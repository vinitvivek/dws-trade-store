"""FastAPI routes for Trade Store API."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models.schemas import (
    TradeCreate,
    TradeResponse,
    HealthCheckResponse,
)
from app.services.trade_service import TradeService
from app.repositories.postgres_repository import PostgresRepository
from app.repositories.mongodb_repository import MongoDBRepository
from app.exceptions import (
    InvalidVersionException,
    InvalidMaturityDateException,
    TradeNotFoundException
)
from app.config import get_settings

router = APIRouter()


def get_trade_service():
    """Dependency to get trade service."""
    postgres_repo = PostgresRepository()
    mongodb_repo = MongoDBRepository()
    return TradeService(postgres_repo, mongodb_repo)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    postgres_repo = PostgresRepository()
    mongodb_repo = MongoDBRepository()
    
    postgres_healthy = postgres_repo.health_check()
    mongodb_healthy = mongodb_repo.health_check()
    
    overall_status = "healthy" if (postgres_healthy and mongodb_healthy) else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        services={
            "postgres": "up" if postgres_healthy else "down",
            "mongodb": "up" if mongodb_healthy else "down"
        }
    )


@router.post("/trades", response_model=TradeResponse, status_code=201)
async def create_trade(
    trade: TradeCreate,
    service: TradeService = Depends(get_trade_service)
):
    """
    Create or update a trade.
    
    Validations:
    - Rejects trades with lower version than existing
    - Accepts trades with same or higher version
    - Rejects trades with maturity date in the past
    """
    try:
        result = service.create_or_update_trade(trade)
        return result
    except InvalidVersionException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidMaturityDateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TradeService = Depends(get_trade_service)
):
    """Get all trades with pagination."""
    return service.get_all_trades(skip, limit)


@router.get("/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: str,
    service: TradeService = Depends(get_trade_service)
):
    """Get a specific trade by ID."""
    try:
        return service.get_trade(trade_id)
    except TradeNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trades/book/{book_id}", response_model=List[TradeResponse])
async def get_trades_by_book(
    book_id: str,
    service: TradeService = Depends(get_trade_service)
):
    """Get all trades for a specific book."""
    return service.get_trades_by_book(book_id)


@router.delete("/trades/{trade_id}")
async def delete_trade(
    trade_id: str,
    service: TradeService = Depends(get_trade_service)
):
    """Delete a trade."""
    success = service.delete_trade(trade_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return {"message": f"Trade {trade_id} deleted successfully"}


@router.get("/statistics")
async def get_statistics(service: TradeService = Depends(get_trade_service)):
    """Get trade statistics."""
    return service.get_statistics()


@router.post("/expire-trades")
async def trigger_expiry_check(service: TradeService = Depends(get_trade_service)):
    """Manually trigger expiry check for trades."""
    count = service.mark_expired_trades()
    return {
        "message": "Expiry check completed",
        "trades_expired": count
    }


@router.get("/audit-logs")
async def get_audit_logs(
    trade_id: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get audit logs from MongoDB."""
    mongodb_repo = MongoDBRepository()
    logs = mongodb_repo.get_audit_logs(trade_id, skip, limit)
    return {"logs": logs, "count": len(logs)}
