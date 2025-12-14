"""DWS - Trade Store Application - Data access repositories."""
from app.repositories.postgres_repository import PostgresRepository
from app.repositories.mongodb_repository import MongoDBRepository

__all__ = ["PostgresRepository", "MongoDBRepository"]