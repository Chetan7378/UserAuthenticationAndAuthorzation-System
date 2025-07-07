# src/security/user_management/user_manager.py
from abc import ABC, abstractmethod
from typing import List, Optional
from models.user_models import UserInfo

class IUserManager(ABC):
    """Abstract Base Class for user management operations."""

    @abstractmethod
    async def get_user_details(self, username: str) -> Optional[UserInfo]:
        """Retrieves details for a specific user."""
        pass

    @abstractmethod
    async def get_all_users_in_group(self, group_name: str) -> List[UserInfo]:
        """Retrieves all users belonging to a specific group."""
        pass

    @abstractmethod
    async def check_group_membership(self, group_name: str, username: str) -> bool:
        """Checks if a user is a member of a specific group."""
        pass