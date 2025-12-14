"""SQLAlchemy models for Trade Store."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Trade(Base):
    """Trade model for PostgreSQL storage."""
    
    __tablename__ = "trades"
    
    trade_id = Column(String(50), primary_key=True, index=True)
    version = Column(Integer, nullable=False)
    counter_party_id = Column(String(50), nullable=False, index=True)
    book_id = Column(String(50), nullable=False, index=True)
    maturity_date = Column(Date, nullable=False, index=True)
    created_date = Column(Date, nullable=False)
    expired = Column(Boolean, default=False, nullable=False, index=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return (
            f"<Trade(trade_id={self.trade_id}, version={self.version}, "
            f"expired={self.expired})>"
        )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "trade_id": self.trade_id,
            "version": self.version,
            "counter_party_id": self.counter_party_id,
            "book_id": self.book_id,
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "expired": self.expired,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
