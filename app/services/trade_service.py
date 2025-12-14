"""Trade service with business logic and validations."""

from datetime import date, datetime
from typing import List, Optional
import logging

from app.models.trade import Trade
from app.models.schemas import TradeCreate, TradeResponse
from app.repositories.postgres_repository import PostgresRepository
from app.repositories.mongodb_repository import MongoDBRepository
from app.exceptions import (
    InvalidVersionException,
    InvalidMaturityDateException,
    TradeNotFoundException
)

logger = logging.getLogger(__name__)


class TradeService:
    """Service for trade business logic."""
    
    def __init__(
        self,
        postgres_repo: PostgresRepository,
        mongodb_repo: MongoDBRepository
    ):
        """Initialize trade service."""
        self.postgres_repo = postgres_repo
        self.mongodb_repo = mongodb_repo
    
    def validate_trade(self, trade_data: TradeCreate, existing_trade: Optional[Trade] = None):
        """
        Validate trade according to business rules:
        1. Lower version trades are rejected
        2. Same version trades replace existing
        3. Maturity date must be >= today
        """
        today = date.today()
        
        # Validation 1 & 2: Version check
        if existing_trade:
            if trade_data.version < existing_trade.version:
                self.mongodb_repo.log_audit(
                    trade_id=trade_data.trade_id,
                    action="VALIDATION_FAILED",
                    details={
                        "reason": "Lower version received",
                        "received_version": trade_data.version,
                        "current_version": existing_trade.version
                    },
                    status="failed"
                )
                raise InvalidVersionException(
                    trade_data.trade_id,
                    trade_data.version,
                    existing_trade.version
                )
        
        # Validation 3: Maturity date check
        if trade_data.maturity_date < today:
            self.mongodb_repo.log_audit(
                trade_id=trade_data.trade_id,
                action="VALIDATION_FAILED",
                details={
                    "reason": "Maturity date in past",
                    "maturity_date": trade_data.maturity_date.isoformat(),
                    "today": today.isoformat()
                },
                status="failed"
            )
            raise InvalidMaturityDateException(
                trade_data.trade_id,
                trade_data.maturity_date.isoformat()
            )
    
    def create_or_update_trade(self, trade_data: TradeCreate) -> TradeResponse:
        """Create or update a trade with validation."""
        try:
            # Get existing trade if any
            existing_trade = self.postgres_repo.get_trade(trade_data.trade_id)
            
            # Validate trade
            self.validate_trade(trade_data, existing_trade)
            
            # Create Trade model
            trade = Trade(
                trade_id=trade_data.trade_id,
                version=trade_data.version,
                counter_party_id=trade_data.counter_party_id,
                book_id=trade_data.book_id,
                maturity_date=trade_data.maturity_date,
                created_date=trade_data.created_date,
                expired=trade_data.expired
            )
            
            # Save to PostgreSQL
            saved_trade = self.postgres_repo.save_trade(trade)
            
            # Log to MongoDB
            action = "UPDATE" if existing_trade else "CREATE"
            self.mongodb_repo.log_audit(
                trade_id=trade_data.trade_id,
                action=action,
                details={
                    "version": trade_data.version,
                    "counter_party_id": trade_data.counter_party_id,
                    "book_id": trade_data.book_id,
                    "maturity_date": trade_data.maturity_date.isoformat(),
                    "previous_version": existing_trade.version if existing_trade else None
                },
                status="success"
            )
            
            logger.info(f"Trade {trade_data.trade_id} {action.lower()}d successfully")
            
            return TradeResponse.model_validate(saved_trade)
            
        except (InvalidVersionException, InvalidMaturityDateException) as e:
            logger.warning(f"Trade validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing trade: {str(e)}")
            self.mongodb_repo.log_audit(
                trade_id=trade_data.trade_id,
                action="ERROR",
                details={"error": str(e)},
                status="failed"
            )
            raise
    
    def get_trade(self, trade_id: str) -> TradeResponse:
        """Get a trade by ID."""
        trade = self.postgres_repo.get_trade(trade_id)
        if not trade:
            raise TradeNotFoundException(trade_id)
        return TradeResponse.model_validate(trade)
    
    def get_all_trades(self, skip: int = 0, limit: int = 100) -> List[TradeResponse]:
        """Get all trades with pagination."""
        trades = self.postgres_repo.get_all_trades(skip, limit)
        return [TradeResponse.model_validate(t) for t in trades]
    
    def get_trades_by_book(self, book_id: str) -> List[TradeResponse]:
        """Get all trades for a specific book."""
        trades = self.postgres_repo.get_trades_by_book(book_id)
        return [TradeResponse.model_validate(t) for t in trades]
    
    def delete_trade(self, trade_id: str) -> bool:
        """Delete a trade."""
        success = self.postgres_repo.delete_trade(trade_id)
        if success:
            self.mongodb_repo.log_audit(
                trade_id=trade_id,
                action="DELETE",
                details={},
                status="success"
            )
        return success
    
    def mark_expired_trades(self) -> int:
        """Mark trades as expired based on maturity date."""
        today = date.today()
        count = self.postgres_repo.mark_expired_trades(today)
        
        if count > 0:
            self.mongodb_repo.log_event(
                event_type="TRADES_EXPIRED",
                data={
                    "count": count,
                    "date": today.isoformat()
                },
                severity="info"
            )
            logger.info(f"Marked {count} trades as expired")
        
        return count
    
    def get_statistics(self) -> dict:
        """Get trade statistics."""
        total = self.postgres_repo.count_trades()
        expired = len(self.postgres_repo.get_expired_trades())
        
        return {
            "total_trades": total,
            "expired_trades": expired,
            "active_trades": total - expired
        }
