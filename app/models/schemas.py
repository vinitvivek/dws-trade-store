"""Pydantic schemas for validation and serialization."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    """Schema for creating a trade."""
    
    trade_id: str = Field(..., min_length=1, max_length=50, description="Trade ID")
    version: int = Field(..., ge=1, description="Trade version")
    counter_party_id: str = Field(..., min_length=1, max_length=50, description="Counter party ID")
    book_id: str = Field(..., min_length=1, max_length=50, description="Book ID")
    maturity_date: date = Field(..., description="Maturity date")
    created_date: date = Field(..., description="Created date")
    expired: bool = Field(default=False, description="Expired flag")
    quantity: int = Field
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "trade_id": "T1",
                    "version": 1,
                    "counter_party_id": "CP-1",
                    "book_id": "B1",
                    "maturity_date": "2025-05-20",
                    "created_date": "2024-12-11",
                    "expired": False
                }
            ]
        }
    }


class TradeResponse(BaseModel):
    """Schema for trade response."""
    
    trade_id: str
    version: int
    counter_party_id: str
    book_id: str
    maturity_date: date
    created_date: date
    expired: bool
    last_updated: Optional[datetime] = None
    quantity == 0
    
    model_config = {"from_attributes": True}


class TradeUpdate(BaseModel):
    """Schema for updating a trade."""
    
    version: Optional[int] = Field(None, ge=1)
    counter_party_id: Optional[str] = Field(None, min_length=1, max_length=50)
    book_id: Optional[str] = Field(None, min_length=1, max_length=50)
    maturity_date: Optional[date] = None
    created_date: Optional[date] = None
    expired: Optional[bool] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str
    timestamp: datetime
    version: str
    services: dict


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str
    detail: str
    timestamp: datetime
