"""Tests for repository layer."""

import pytest
from datetime import date, timedelta

from app.models.trade import Trade


class TestPostgresRepository:
    """Test cases for PostgreSQL repository."""
    
    def test_save_new_trade(self, postgres_repo):
        """Test saving a new trade."""
        trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False
        )
        
        result = postgres_repo.save_trade(trade)
        
        assert result.trade_id == "T1"
        assert result.version == 1
    
    def test_update_existing_trade(self, postgres_repo):
        """Test updating an existing trade."""
        trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False
        )
        postgres_repo.save_trade(trade)
        
        # Update trade
        trade.version = 2
        trade.counter_party_id = "CP-2"
        result = postgres_repo.save_trade(trade)
        
        assert result.version == 2
        assert result.counter_party_id == "CP-2"
    
    def test_get_trade(self, postgres_repo):
        """Test retrieving a trade."""
        trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False
        )
        postgres_repo.save_trade(trade)
        
        result = postgres_repo.get_trade("T1")
        
        assert result is not None
        assert result.trade_id == "T1"
    
    def test_get_nonexistent_trade(self, postgres_repo):
        """Test getting non-existent trade returns None."""
        result = postgres_repo.get_trade("NONEXISTENT")
        
        assert result is None
    
    def test_get_all_trades(self, postgres_repo):
        """Test getting all trades."""
        for i in range(3):
            trade = Trade(
                trade_id=f"T{i+1}",
                version=1,
                counter_party_id=f"CP-{i+1}",
                book_id="B1",
                maturity_date=date.today() + timedelta(days=30),
                created_date=date.today(),
                expired=False
            )
            postgres_repo.save_trade(trade)
        
        results = postgres_repo.get_all_trades()
        
        assert len(results) == 3
    
    def test_get_trades_by_book(self, postgres_repo):
        """Test getting trades by book ID."""
        # Create trades with different books
        for i in range(3):
            book_id = "B1" if i < 2 else "B2"
            trade = Trade(
                trade_id=f"T{i+1}",
                version=1,
                counter_party_id=f"CP-{i+1}",
                book_id=book_id,
                maturity_date=date.today() + timedelta(days=30),
                created_date=date.today(),
                expired=False
            )
            postgres_repo.save_trade(trade)
        
        results = postgres_repo.get_trades_by_book("B1")
        
        assert len(results) == 2
        assert all(t.book_id == "B1" for t in results)
    
    def test_get_expired_trades(self, postgres_repo):
        """Test getting expired trades."""
        # Create expired and active trades
        expired_trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() - timedelta(days=1),
            created_date=date.today(),
            expired=True
        )
        active_trade = Trade(
            trade_id="T2",
            version=1,
            counter_party_id="CP-2",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False
        )
        
        postgres_repo.save_trade(expired_trade)
        postgres_repo.save_trade(active_trade)
        
        results = postgres_repo.get_expired_trades()
        
        assert len(results) == 1
        assert results[0].trade_id == "T1"
    
    def test_delete_trade(self, postgres_repo):
        """Test deleting a trade."""
        trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False
        )
        postgres_repo.save_trade(trade)
        
        success = postgres_repo.delete_trade("T1")
        
        assert success is True
        assert postgres_repo.get_trade("T1") is None
    
    def test_mark_expired_trades(self, postgres_repo):
        """Test marking trades as expired."""
        # Create trade with past maturity
        trade = Trade(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() - timedelta(days=1),
            created_date=date.today() - timedelta(days=2),
            expired=False
        )
        postgres_repo.save_trade(trade)
        
        count = postgres_repo.mark_expired_trades(date.today())
        
        assert count == 1
        
        updated_trade = postgres_repo.get_trade("T1")
        assert updated_trade.expired is True
    
    def test_count_trades(self, postgres_repo):
        """Test counting trades."""
        for i in range(3):
            trade = Trade(
                trade_id=f"T{i+1}",
                version=1,
                counter_party_id=f"CP-{i+1}",
                book_id="B1",
                maturity_date=date.today() + timedelta(days=30),
                created_date=date.today(),
                expired=False
            )
            postgres_repo.save_trade(trade)
        
        count = postgres_repo.count_trades()
        
        assert count == 3
    
    def test_health_check(self, postgres_repo):
        """Test database health check."""
        result = postgres_repo.health_check()
        
        assert result is True


class TestMongoDBRepository:
    """Test cases for MongoDB repository."""
    
    def test_log_audit(self, mongodb_repo):
        """Test logging audit entry."""
        result = mongodb_repo.log_audit(
            trade_id="T1",
            action="CREATE",
            details={"version": 1},
            status="success"
        )
        
        assert result == "mock_id"
        assert len(mongodb_repo.audit_logs) == 1
    
    def test_log_event(self, mongodb_repo):
        """Test logging system event."""
        result = mongodb_repo.log_event(
            event_type="TRADES_EXPIRED",
            data={"count": 5},
            severity="info"
        )
        
        assert result == "mock_id"
        assert len(mongodb_repo.events) == 1
    
    def test_get_audit_logs(self, mongodb_repo):
        """Test retrieving audit logs."""
        mongodb_repo.log_audit("T1", "CREATE", {})
        mongodb_repo.log_audit("T2", "UPDATE", {})
        
        logs = mongodb_repo.get_audit_logs()
        
        assert len(logs) == 2
    
    def test_get_audit_logs_by_trade_id(self, mongodb_repo):
        """Test retrieving audit logs filtered by trade ID."""
        mongodb_repo.log_audit("T1", "CREATE", {})
        mongodb_repo.log_audit("T1", "UPDATE", {})
        mongodb_repo.log_audit("T2", "CREATE", {})
        
        logs = mongodb_repo.get_audit_logs(trade_id="T1")
        
        assert len(logs) == 2
        assert all(log["trade_id"] == "T1" for log in logs)