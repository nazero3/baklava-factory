from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_KEY = "dev-insecure-change-me"


class Settings(BaseSettings):
    secret_key: str = _INSECURE_DEFAULT_KEY
    database_url: str = "sqlite:///./mvp.db"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    bootstrap_admin: str | None = None
    env: str = "development"
    login_rate_limit: str = "10/minute"
    cors_allow_origins: str = ""
    stock_adjustment_auto_approve_kg: float = 1.0
    transfer_diff_auto_approve_kg: float = 0.2
    max_csv_upload_bytes: int = 5 * 1024 * 1024  # 5 MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def check_production_secrets(self) -> "Settings":
        if self.env.lower() == "production" and self.secret_key == _INSECURE_DEFAULT_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a strong value in production. "
                "Set the SECRET_KEY environment variable."
            )
        return self

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_allow_origins.strip():
            return []
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()
