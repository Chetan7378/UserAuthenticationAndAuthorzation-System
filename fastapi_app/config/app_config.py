# src/config/app_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    """Base application configuration."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "SecureAuthService"
    DEBUG_MODE: bool = False