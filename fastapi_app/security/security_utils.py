# src/security/security_utils.py
import re
from exceptions.custom_exceptions import InputValidationError
from constants.error_messages import ErrorMessages

def validate_login_input(username: str, password: str):
    """Validates username and password for basic security."""
    if not username or not password:
        raise InputValidationError(detail=ErrorMessages.MISSING_INPUT)
    if len(username) < 3 or len(password) < 8:
        raise InputValidationError(detail=ErrorMessages.INVALID_USERNAME_OR_PASSWORD)
    # Add more complex regex checks if needed

def is_safe_ldap_string(input_str: str):
    """
    Checks if a string is safe for LDAP queries to prevent injection.
    This is a basic check; for production, consider a dedicated LDAP escaping library.
    """
    if not input_str:
        raise InputValidationError(detail=ErrorMessages.MISSING_INPUT)
    # Disallow common LDAP special characters if not explicitly escaped
    # This regex allows alphanumeric, spaces, hyphens, and underscores.
    # More complex characters like '*' or '()' might be valid in some DNs,
    # but for simple searches, it's safer to restrict.
    if not re.match(r"^[a-zA-Z0-9\s\-_.]+$", input_str):
        raise InputValidationError(detail=ErrorMessages.LDAP_INJECTION_DETECTED)
    return True