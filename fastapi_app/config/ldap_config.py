# src/config/ldap_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class LdapConfig(BaseSettings):
    """
    LDAP specific configuration.

    LDAP_SERVER: Replace with your actual LDAP server URL
    LDAP_BASE_DN: Replace with your actual base DN
    - Set LDAP_GROUP_DN to your actual group DN (replace with your actual group DN).
    - LDAP_AUTO_BIND enables auto-bind connection.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LDAP_SERVER: str = "ldap://localhost:10389"
    LDAP_BASE_DN: str = "dc=example,dc=com"
    LDAP_GROUP_DN: str = "ou=groups,dc=example,dc=com"
    LDAP_AUTO_BIND: bool = True