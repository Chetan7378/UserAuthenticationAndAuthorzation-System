# src/security/jwt/jwt_manager.py
import time
import jwt
import logging
# REMOVE: from fastapi import Depends  <--- Not needed here anymore

from config.jwt_config import JwtConfig
from models.auth_models import TokenResponse
from constants.auth_constants import AuthConstants, TokenType
from constants.error_messages import ErrorMessages
from exceptions.custom_exceptions import (
    TokenExpiredError, TokenRevokedError, RefreshTokenExpired, RefreshTokenRevoked, RefreshTokenInvalid
)
from security.jwt.token_blacklist import TokenBlacklist

logger = logging.getLogger(__name__)

# The oauth2_scheme should NOT be here. It's a FastAPI dependency,
# and will be defined in src/dependencies/container.py

class JwtManager:
    """Manages JWT token creation, verification, and revocation."""
    def __init__(self, config: JwtConfig, blacklist: TokenBlacklist):
        self.secret_key = config.JWT_SECRET
        self.algorithm = config.JWT_ALGO
        self.access_token_expiration = config.JWT_EXPIRATION_SECONDS
        self.refresh_token_expiration = config.JWT_REFRESH_EXPIRATION_SECONDS
        self.blacklist = blacklist

    async def create_tokens(self, data: dict) -> TokenResponse:
        """Creates access and refresh tokens."""
        now = int(time.time())
        access_payload = self._create_payload(data, now, self.access_token_expiration, TokenType.ACCESS)
        refresh_payload = self._create_payload(data, now, self.refresh_token_expiration, TokenType.REFRESH)

        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)

        return TokenResponse(
            access_token=access_token,
            token_type=AuthConstants.TOKEN_TYPE_BEARER,
            refresh_token=refresh_token
        )

    def _create_payload(self, data: dict, now: int, expiration_seconds: int, token_type: TokenType) -> dict:
        """Helper to create JWT payload."""
        user_cn = data.get(AuthConstants.CN_ATTRIBUTE) or data.get(AuthConstants.UID_ATTRIBUTE)
        jti_prefix = f"{user_cn}:{token_type.value}" if user_cn else f"anonymous:{token_type.value}"
        payload = {
            AuthConstants.EXP_KEY: now + expiration_seconds,
            AuthConstants.IAT_KEY: now,
            AuthConstants.SUB_KEY: user_cn,
            AuthConstants.JTI_KEY: f"{jti_prefix}:{now}",
            AuthConstants.USER_DATA_KEY: data,
            AuthConstants.SCOPE_KEY: token_type.value
        }
        return payload

    # Renamed to clearly indicate it's the logic, not a FastAPI dependency
    async def verify_access_token_logic(self, token: str) -> dict:
        """Verifies an access token string and returns its payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return self._check_payload_status(payload, TokenType.ACCESS)
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired.")
            raise TokenExpiredError()
        except jwt.DecodeError:
            logger.warning("Invalid access token format or signature.")
            raise TokenRevokedError(detail=ErrorMessages.INVALID_TOKEN)
        except Exception as e:
            logger.error(f"Unexpected error during access token verification: {e}")
            raise TokenRevokedError(detail=ErrorMessages.INVALID_TOKEN)

    async def verify_refresh_token(self, refresh_token: str) -> dict:
        """Verifies a refresh token and returns its payload."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            return self._check_payload_status(payload, TokenType.REFRESH)
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token expired.")
            raise RefreshTokenExpired()
        except jwt.DecodeError:
            logger.warning("Invalid refresh token format or signature.")
            raise RefreshTokenInvalid()
        except Exception as e:
            logger.error(f"Unexpected error during refresh token verification: {e}")
            raise RefreshTokenInvalid()

    def _check_payload_status(self, payload: dict, expected_type: TokenType) -> dict:
        """Checks JTI blacklist and token type."""
        jti = payload.get(AuthConstants.JTI_KEY)
        token_type = payload.get(AuthConstants.SCOPE_KEY)

        if not jti or self.blacklist.is_blacklisted(jti):
            logger.warning(f"Token (JTI: {jti}) is blacklisted or missing JTI.")
            raise TokenRevokedError(detail=ErrorMessages.TOKEN_REVOKED)

        if token_type != expected_type.value:
            logger.warning(f"Token type mismatch. Expected {expected_type.value}, got {token_type}.")
            raise TokenRevokedError(detail=ErrorMessages.INVALID_TOKEN)

        return payload

    # Renamed to clearly indicate it's the logic, not a FastAPI dependency
    async def revoke_access_token_logic(self, token: str):        
        """Revokes an access token by adding its JTI to the blacklist."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            jti = payload.get(AuthConstants.JTI_KEY)
            if jti:
                self.blacklist.add(jti)
                logger.info(f"Token JTI: {jti} revoked successfully.")
                return {"message": "Token revoked successfully"}
            else:
                logger.warning("Attempted to revoke token without JTI.")
                raise TokenRevokedError(detail="Token missing identifier (JTI).")
        except jwt.DecodeError:
            logger.warning("Attempted to revoke invalid token.")
            raise TokenRevokedError(detail=ErrorMessages.INVALID_TOKEN)
        except Exception as e:
            logger.error(f"Unexpected error during token revocation: {e}")
            raise TokenRevokedError(detail=ErrorMessages.UNEXPECTED_ERROR)

    async def revoke_refresh_token(self, refresh_token: str):
        """Revokes a refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            jti = payload.get(AuthConstants.JTI_KEY)
            token_type = payload.get(AuthConstants.SCOPE_KEY)
            if token_type != TokenType.REFRESH.value:
                raise RefreshTokenInvalid(detail="Provided token is not a refresh token.")

            if jti:
                self.blacklist.add(jti)
                logger.info(f"Refresh Token JTI: {jti} revoked successfully.")
                return {"message": "Refresh token revoked successfully"}
            else:
                logger.warning("Attempted to revoke refresh token without JTI.")
                raise RefreshTokenInvalid(detail="Refresh token missing identifier (JTI).")
        except jwt.DecodeError:
            logger.warning("Attempted to revoke invalid refresh token.")
            raise RefreshTokenInvalid()
        except Exception as e:
            logger.error(f"Unexpected error during refresh token revocation: {e}")
            raise RefreshTokenInvalid(detail=ErrorMessages.UNEXPECTED_ERROR)