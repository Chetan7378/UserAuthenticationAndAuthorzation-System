# This is a simple in-memory blacklist for demonstration purposes.
# For production, use a persistent store like Redis for scalability and reliability.

class TokenBlacklist:
    """Manages blacklisted JWTs (JTI values)."""
    _instance = None
    _blacklist = set() # Stores JTI values

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenBlacklist, cls).__new__(cls)
        return cls._instance

    def add(self, jti: str):
        """Adds a JTI to the blacklist."""
        if jti:
            self._blacklist.add(jti)

    def is_blacklisted(self, jti: str) -> bool:
        """Checks if a JTI is in the blacklist."""
        return jti in self._blacklist

    def remove_expired(self):
        """
        In a real scenario, this would periodically clean up expired JTIs
        from a persistent store. For in-memory, it's less critical unless        memory becomes an issue.
        """
        # Placeholder for future cleanup logic based on token expiration
        pass