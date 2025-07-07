from config.ldap_config import LdapConfig
from security.authentication.auth_strategy import IAuthStrategy
from security.authentication.ldap_strategy import LdapAuthStrategy
from security.connection.ldap_connection_manager import LdapConnectionManager
from constants.error_messages import ErrorMessages
class AuthFactory:
    """Factory for creating authentication strategies."""

    @staticmethod
    def create_auth_strategy(provider_type: str,ldap_config: LdapConfig,
                             ldap_conn_manager: LdapConnectionManager) -> IAuthStrategy:
        """
        Creates an authentication strategy based on the provider type.
        Extensible for other providers (Okta, AWS, Azure, etc.).
        """
        if provider_type.lower() == "ldap":
            return LdapAuthStrategy(ldap_config, ldap_conn_manager)
        # Add other authentication providers here as needed
        else:
            raise ValueError(f"{ErrorMessages.UNSUPPORTED_AUTH_PROVIDER}:{provider_type}")