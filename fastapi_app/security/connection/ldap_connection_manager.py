# src/security/connection/ldap_connection_manager.py
import logging
from typing import List, Any
from ldap3 import Server, Connection, ALL
from config.ldap_config import LdapConfig
from security.connection.connection_manager import IConnectionManager
from exceptions.custom_exceptions import LDAPBindError
from constants.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

class LdapConnectionManager(IConnectionManager):
    """LDAP specific implementation of IConnectionManager."""
    def __init__(self, config: LdapConfig):
        self.ldap_server = config.LDAP_SERVER
        self.auth_bind = config.LDAP_AUTO_BIND

    def connect(self, user_dn: str = None, password: str = None) -> Connection:
        """Establishes and returns an LDAP connection."""        
        try:
            if not user_dn or not password:
                return Connection(Server(self.ldap_server, get_info=ALL), auto_bind=self.auth_bind)
            server = Server(self.ldap_server, get_info=ALL)
            conn = Connection(server, user=user_dn, password=password, auto_bind=self.auth_bind)            
            if not self.auth_bind and not conn.bind():
                logger.error(f"Failed to bind to LDAP server for user: {user_dn}")
                raise LDAPBindError(detail=ErrorMessages.LDAP_BIND_FAILED)
            return conn
        except Exception as e:
            logger.exception(f"Error connecting to LDAP server: {e}")
            raise LDAPBindError(detail=ErrorMessages.LDAP_BIND_FAILED)

    def disconnect(self, connection: Connection):
        """Closes an LDAP connection."""
        if connection and connection.bound:
            connection.unbind()

    def search(self, connection: Connection, search_base: str, search_filter: str, attributes: List[str]) -> List[Any]:
        """Performs an LDAP search operation."""
        try:
            connection.search(search_base=search_base, search_filter=search_filter, attributes=attributes)
            return list(connection.entries)
        except Exception as e:
            logger.exception(f"LDAP search failed: {e}")
            # Re-raise as a generic LDAP error, specific handling might be in higher layers
            raise LDAPBindError(detail=ErrorMessages.LDAP_AUTH_ERROR)