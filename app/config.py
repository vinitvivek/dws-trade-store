"""Configuration management for Trade Store Application."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "DWS Trade Store"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # PostgreSQL (Structured Data)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "dws_tradestore"
    POSTGRES_USER: str = "dws_user"
    POSTGRES_PASSWORD: str = "dwsuser1234"
    
    # MongoDB (Unstructured Data - Audit Logs)
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "mdws_tradestore"
    MONGODB_USER: str = "dws_user"
    MONGODB_PASSWORD: str = "dwsuser1234"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "dws_trade_store"
    KAFKA_GROUP_ID: str = "trade-consumer-group"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    
    # Scheduler
    EXPIRY_CHECK_INTERVAL_MINUTES: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return (
                f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
                f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
            )
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
