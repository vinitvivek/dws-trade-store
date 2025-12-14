"""Custom exceptions for Trade Store Application."""


class TradeStoreException(Exception):
    """Base exception for trade store."""
    pass


class InvalidVersionException(TradeStoreException):
    """Raised when a trade version is lower than the existing version."""
    
    def __init__(self, trade_id: str, received_version: int, current_version: int):
        self.trade_id = trade_id
        self.received_version = received_version
        self.current_version = current_version
        super().__init__(
            f"Trade {trade_id}: Received version {received_version} is lower "
            f"than current version {current_version}"
        )


class InvalidMaturityDateException(TradeStoreException):
    """Raised when maturity date is earlier than today."""
    
    def __init__(self, trade_id: str, maturity_date: str):
        self.trade_id = trade_id
        self.maturity_date = maturity_date
        super().__init__(
            f"Trade {trade_id}: Maturity date {maturity_date} is earlier than today"
        )


class TradeNotFoundException(TradeStoreException):
    """Raised when a trade is not found."""
    
    def __init__(self, trade_id: str):
        self.trade_id = trade_id
        super().__init__(f"Trade {trade_id} not found")
