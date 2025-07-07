# src/security/connection/connection_manager.py
from abc import ABC, abstractmethod
from typing import Any, List

class IConnectionManager(ABC):
    """Abstract Base Class for connection managers."""

    @abstractmethod
    def connect(self) -> Any:
        """Establishes and returns a connection."""
        pass

    @abstractmethod
    def disconnect(self, connection: Any):
        """Closes a given connection."""
        pass

    @abstractmethod
    def search(self, connection: Any, search_base: str, search_filter: str, attributes: List[str]) -> List[Any]:
        """Performs a search operation."""
        pass