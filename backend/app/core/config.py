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


settings = Settings()
