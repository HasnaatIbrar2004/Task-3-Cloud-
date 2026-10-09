from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    database_url: str = "sqlite:///./app.db"

    mfa_expiration_minutes: int = 5
    mfa_max_attempts: int = 5

    log_level: str = "INFO"
    log_dir: str = "logs"

    smtp_host: str = "smtp.ethereal.email"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "voting-system@example.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
