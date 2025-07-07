from abc import ABC, abstractmethod
from typing import Optional
from models.user_models import UserInfo

class IAuthStrategy(ABC):
    """Abstract Base Class for authentication strategies."""

    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[UserInfo]:
        """
        Authenticates a user and returns their information if successful.
        Returns None if authentication fails.
        """
        pass