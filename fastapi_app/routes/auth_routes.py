# src/api/v1/auth_routes.py
from fastapi import Response
from typing import Dict
import logging
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models.auth_models import TokenResponse, RefreshTokenRequest
from dependencies.container import get_ldap_manager, get_jwt_manager, revoke_access_token_dependency, verify_access_token
from security.ldap_manager import LdapManager
from security.jwt.jwt_manager import JwtManager
from security.security_utils import validate_login_input
from exceptions.custom_exceptions import InvalidCredentialsError, AuthException

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    ldap_mgr: LdapManager = Depends(get_ldap_manager),
    jwt_mgr: JwtManager = Depends(get_jwt_manager)):
    try:
        validate_login_input(form_data.username, form_data.password)
        user = await ldap_mgr.authenticate_user(form_data.username, form_data.password)
        tokens = await jwt_mgr.create_tokens(user.dict())
        logger.info(f"{form_data.username} logged in successfully.")
        return tokens
    except AuthException as e:
        logger.warning(f"Login failed for {form_data.username}: {e.detail}")
        raise e # Re-raise custom exceptions directly
    except Exception as e:
        logger.exception(f"Unexpected error during login for {form_data.username}: {e}")
        raise InvalidCredentialsError() # Generalize unexpected errors to protect info


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    # Use the new dependency for revocation
    token_revocation_response: dict = Depends(revoke_access_token_dependency)
):
    """
    Revokes the current access token, effectively logging out the user.
    """
    logger.info("User requested logout (access token revoked).")
    return token_revocation_response
    

@router.post("/refresh-token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    jwt_mgr: JwtManager = Depends(get_jwt_manager)):  
    try:        
        payload = await jwt_mgr.verify_refresh_token(request.refresh_token)
        
        await jwt_mgr.revoke_refresh_token(request.refresh_token)
        
        user_data = payload.get("user", {})
        new_tokens = await jwt_mgr.create_tokens(user_data)
        logger.info(f"Tokens refreshed for user: {payload.get('sub')}")
        return new_tokens
    except AuthException as e:
        logger.warning(f"Refresh token failed: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error during token refresh: {e}")
        raise AuthException(detail="Failed to refresh token.")