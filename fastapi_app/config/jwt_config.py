# src/config/jwt_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from constants.auth_constants import AuthConstants

class JwtConfig(BaseSettings):
    """JWT specific configuration."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_SECRET: str="your_jwt_secret_key"  # Replace with your actual secret key
    JWT_ALGO: str = AuthConstants.JWT_ALGORITHM
    JWT_EXPIRATION_SECONDS: int = 1800  # half hour for access token
    JWT_REFRESH_EXPIRATION_SECONDS: int = 86400 # 1 day for refresh token