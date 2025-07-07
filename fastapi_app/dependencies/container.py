# src/dependencies/container.py
from functools import lru_cache
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer # <-- Import OAuth2PasswordBearer here

from security.jwt.token_blacklist import TokenBlacklist
from config.app_config import AppConfig
from config.jwt_config import JwtConfig
from config.ldap_config import LdapConfig
from security.jwt.jwt_manager import JwtManager # <-- Import the JwtManager class
from security.jwt.token_blacklist import TokenBlacklist
from security.connection.ldap_connection_manager import LdapConnectionManager
from security.authentication.auth_factory import AuthFactory
from security.ldap_manager import LdapManager
from security.authentication.auth_strategy import IAuthStrategy
from security.user_management.user_manager import IUserManager
from security.user_management.ldap_user_manager import LdapUserManager

# Define the OAuth2PasswordBearer scheme once globally in the dependency container
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@lru_cache()
def get_app_config() -> AppConfig:
    """Provides AppConfig instance (cached)."""
    return AppConfig()

@lru_cache()
def get_jwt_config() -> JwtConfig:
    """Provides JwtConfig instance (cached)."""    
    return JwtConfig()

@lru_cache()
def get_ldap_config() -> LdapConfig:
    """Provides LdapConfig instance (cached)."""
    return LdapConfig()@lru_cache()
def get_token_blacklist() -> TokenBlacklist:
    """Provides TokenBlacklist instance (singleton)."""
    return TokenBlacklist()

@lru_cache()
def get_jwt_manager(
    jwt_config: JwtConfig = Depends(get_jwt_config),
    blacklist: TokenBlacklist = Depends(get_token_blacklist)
) -> JwtManager:
    """Provides JwtManager instance."""
    return JwtManager(jwt_config, blacklist)

@lru_cache()
def get_ldap_connection_manager(
    ldap_config: LdapConfig = Depends(get_ldap_config)
) -> LdapConnectionManager:
    """Provides LdapConnectionManager instance."""
    return LdapConnectionManager(ldap_config)

@lru_cache()
def get_ldap_auth_strategy(
    ldap_config: LdapConfig = Depends(get_ldap_config),
    ldap_conn_manager: LdapConnectionManager = Depends(get_ldap_connection_manager)
) -> IAuthStrategy:
    """Provides LdapAuthStrategy instance."""
    return AuthFactory.create_auth_strategy("ldap", ldap_config, ldap_conn_manager)

@lru_cache()
def get_ldap_user_manager(
    ldap_config: LdapConfig = Depends(get_ldap_config),
    ldap_conn_manager: LdapConnectionManager = Depends(get_ldap_connection_manager)
) -> IUserManager:
    """Provides LdapUserManager instance."""
    return LdapUserManager(ldap_config, ldap_conn_manager)

@lru_cache()
def get_ldap_manager(
    auth_strategy: IAuthStrategy = Depends(get_ldap_auth_strategy),
    user_manager: IUserManager = Depends(get_ldap_user_manager)
) -> LdapManager:
    """Provides LdapManager instance (facade)."""
    return LdapManager(auth_strategy, user_manager)

# Dependency for token verification in protected routes
async def verify_access_token(
    token: str = Depends(oauth2_scheme), # <-- Get the token string from the header
    jwt_mgr: JwtManager = Depends(get_jwt_manager) # <-- Get the JwtManager instance
):
    """Dependency to verify access token and return payload."""
    # Call the logic method on the JwtManager instance
    return await jwt_mgr.verify_access_token_logic(token)

# New dependency for token revocation (e.g., for logout)
async def revoke_access_token_dependency(
    token: str = Depends(oauth2_scheme), # <-- Get the token string from the header
    jwt_mgr: JwtManager = Depends(get_jwt_manager) # <-- Get the JwtManager instance
):
    """Dependency to revoke access token."""
    # Call the logic method on the JwtManager instance
    return await jwt_mgr.revoke_access_token_logic(token)