# src/exceptions/custom_exceptions.py
from fastapi import HTTPException, status
from constants.error_messages import ErrorMessages

class AuthException(HTTPException):
    """Base class for authentication-related exceptions."""
    def __init__(self, detail: str = ErrorMessages.UNEXPECTED_ERROR, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)

class InvalidCredentialsError(AuthException):
    def __init__(self, detail: str = ErrorMessages.INVALID_CREDENTIALS):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class TokenExpiredError(AuthException):
    def __init__(self, detail: str = ErrorMessages.TOKEN_EXPIRED):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class TokenRevokedError(AuthException):
    def __init__(self, detail: str = ErrorMessages.TOKEN_REVOKED):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class LDAPBindError(AuthException):
    def __init__(self, detail: str = ErrorMessages.LDAP_BIND_FAILED):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class GroupNotFound(AuthException):
    def __init__(self, detail: str = ErrorMessages.GROUP_NOT_FOUND):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class LDAPAuthError(AuthException):
    def __init__(self, detail: str = ErrorMessages.LDAP_AUTH_ERROR):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class InputValidationError(AuthException):
    def __init__(self, detail: str = ErrorMessages.MISSING_INPUT):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class RateLimitExceeded(AuthException):
    def __init__(self, detail: str = ErrorMessages.RATE_LIMIT_EXCEEDED):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)

class RefreshTokenExpired(AuthException):
    def __init__(self, detail: str = ErrorMessages.REFRESH_TOKEN_EXPIRED):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class RefreshTokenInvalid(AuthException):
    def __init__(self, detail: str = ErrorMessages.REFRESH_TOKEN_INVALID):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class RefreshTokenRevoked(AuthException):
    def __init__(self, detail: str = ErrorMessages.REFRESH_TOKEN_REVOKED):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)