"""Pytest configuration and fixtures."""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.trade import Base, Trade
from app.repositories.postgres_repository import PostgresRepository
from app.repositories.mongodb_repository import MongoDBRepository
from app.services.trade_service import TradeService
from app.models.schemas import TradeCreate


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def postgres_repo(test_db_engine):
    """Create PostgreSQL repository with test database."""
    repo = PostgresRepository(connection_url="sqlite:///:memory:")
    repo.create_tables()
    yield repo
    repo.drop_tables()


@pytest.fixture(scope="function")
def mongodb_repo(monkeypatch):
    """Create MongoDB repository mock."""
    class MockMongoDBRepository:
        def __init__(self):
            self.audit_logs = []
            self.events = []
        
        def log_audit(self, trade_id, action, details, status="success"):
            self.audit_logs.append({
                "trade_id": trade_id,
                "action": action,
                "details": details,
                "status": status
            })
            return "mock_id"
        
        def log_event(self, event_type, data, severity="info"):
            self.events.append({
                "event_type": event_type,
                "data": data,
                "severity": severity
            })
            return "mock_id"
        
        def get_audit_logs(self, trade_id=None, skip=0, limit=100):
            if trade_id:
                return [log for log in self.audit_logs if log["trade_id"] == trade_id]
            return self.audit_logs[skip:skip+limit]
        
        def health_check(self):
            return True
    
    return MockMongoDBRepository()


@pytest.fixture(scope="function")
def trade_service(postgres_repo, mongodb_repo):
    """Create trade service with test repositories."""
    return TradeService(postgres_repo, mongodb_repo)


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing."""
    today = date.today()
    future_date = today + timedelta(days=30)
    
    return TradeCreate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=future_date,
        created_date=today,
        expired=False
    )


@pytest.fixture
def sample_trade_dict():
    """Sample trade dictionary for testing."""
    today = date.today()
    future_date = today + timedelta(days=30)
    
    return {
        "trade_id": "T1",
        "version": 1,
        "counter_party_id": "CP-1",
        "book_id": "B1",
        "maturity_date": future_date.isoformat(),
        "created_date": today.isoformat(),
        "expired": False
    }


@pytest.fixture
def multiple_trades():
    """Multiple sample trades for testing."""
    today = date.today()
    future_date = today + timedelta(days=30)
    past_date = today - timedelta(days=10)
    
    return [
        TradeCreate(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=future_date,
            created_date=today,
            expired=False
        ),
        TradeCreate(
            trade_id="T2",
            version=2,
            counter_party_id="CP-2",
            book_id="B1",
            maturity_date=future_date,
            created_date=today,
            expired=False
        ),
        TradeCreate(
            trade_id="T3",
            version=1,
            counter_party_id="CP-3",
            book_id="B2",
            maturity_date=past_date,
            created_date=today,
            expired=True
        )
    ]