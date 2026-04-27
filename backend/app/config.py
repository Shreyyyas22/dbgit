from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, SecretStr

class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"

    # Database URLs
    meta_database_url: PostgresDsn
    target_database_url: PostgresDsn | None = None

    # Redis Cache
    redis_url: str = "redis://localhost:6379/0"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # Auth
    jwt_secret_key: SecretStr = SecretStr("change_me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
