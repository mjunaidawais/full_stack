from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "restaurant-backend"
    env: str = "dev"

    mongodb_uri: str
    mongodb_db: str = "restaurant"

    redis_url: str

    jwt_issuer: str = "restaurant-backend"
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 1209600
    jwt_secret: str

    cors_origins: str = ""

    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()

