import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentinel"
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@postgres:5432/sentinel"
    database_url_sync: str = "postgresql://sentinel:sentinel@postgres:5432/sentinel"
    anthropic_api_key: str = ""
    null_spike_threshold: float = 0.15
    statistical_anomaly_std_devs: float = 3.0
    scan_interval_seconds: int = 60

    class Config:
        env_file = ".env"

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Strip params that asyncpg doesn't support
        for param in ["channel_binding=require", "sslmode=require"]:
            url = url.replace(f"&{param}", "").replace(f"?{param}&", "?").replace(f"?{param}", "")
        return url

    @property
    def sync_database_url(self) -> str:
        url = self.database_url_sync or self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if "+asyncpg" in url:
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url


settings = Settings()
