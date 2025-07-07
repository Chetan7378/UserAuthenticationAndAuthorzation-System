# src/security/authentication/ldap_strategy.py
import logging
import asyncio
from ldap3 import Connection
from config.ldap_config import LdapConfig
from models.user_models import UserInfo
from security.authentication.auth_strategy import IAuthStrategy
from security.connection.ldap_connection_manager import LdapConnectionManager
from exceptions.custom_exceptions import InvalidCredentialsError, LDAPAuthError
from constants.error_messages import ErrorMessages
from constants.ldap_constants import LdapAttributes

logger = logging.getLogger(__name__)

class LdapAuthStrategy(IAuthStrategy):
    """LDAP specific authentication strategy."""
    def __init__(self, config: LdapConfig, conn_manager: LdapConnectionManager):
        self.base_dn = config.LDAP_BASE_DN
        self.conn_manager = conn_manager

    async def authenticate(self, username: str, password: str) -> UserInfo:
    
        return await asyncio.to_thread(self._authenticate_sync, username, password)    
    def _authenticate_sync(self, username: str, password: str) -> UserInfo:
        
        conn: Connection = None
        try:
            user_dn = f"{LdapAttributes.CN}={username},{self.base_dn}"
            conn = self.conn_manager.connect(user_dn=user_dn, password=password)

            # If bind successful, verify user exists and fetch attributes
            entries = self.conn_manager.search(
                conn, self.base_dn, f'({LdapAttributes.CN}={username})',
                [LdapAttributes.CN, LdapAttributes.MAIL, LdapAttributes.SN, LdapAttributes.UID]
            )

            if not entries:
                logger.warning(f"User {username} not found after successful bind.")
                raise InvalidCredentialsError(detail=ErrorMessages.USER_NOT_FOUND)

            entry = entries[0]
            return UserInfo(
                cn=getattr(entry, LdapAttributes.CN.value, None).value,
                mail=getattr(entry, LdapAttributes.MAIL.value, None).value,
                sn=getattr(entry, LdapAttributes.SN.value, None).value,
                uid=getattr(entry, LdapAttributes.UID.value, None).value
            )
        except InvalidCredentialsError:
            raise # Re-raise known authentication failures
        except Exception as e:
            logger.exception(f"Unexpected error during LDAP authentication for {username}: {e}")
            raise LDAPAuthError(detail=ErrorMessages.LDAP_AUTH_ERROR)
        finally:
            self.conn_manager.disconnect(conn)