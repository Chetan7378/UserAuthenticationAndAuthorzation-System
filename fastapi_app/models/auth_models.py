# src/models/auth_models.py
from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    """Pydantic model for JWT token response."""
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class LoginRequest(BaseModel):
    """Pydantic model for login request."""
    username: str
    password: str

class RefreshTokenRequest(BaseModel):    
    """Pydantic model for refresh token request."""
    refresh_token: str