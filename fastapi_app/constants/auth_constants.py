# src/constants/auth_constants.py
from enum import Enum

class AuthConstants(str, Enum):
    """Constants related to authentication."""
    JWT_ALGORITHM = "HS256"
    TOKEN_TYPE_BEARER = "bearer"
    ACCESS_TOKEN_KEY = "access_token"
    REFRESH_TOKEN_KEY = "refresh_token"
    TOKEN_TYPE_KEY = "token_type"
    SUB_KEY = "sub" # Subject (username/cn)
    JTI_KEY = "jti" # JWT ID (for unique token identification and revocation)
    EXP_KEY = "exp" # Expiration timestamp
    IAT_KEY = "iat" # Issued at timestamp
    USER_DATA_KEY = "user" # Custom key for user data in payload
    ROLE_KEY = "role" # User role in the system

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"