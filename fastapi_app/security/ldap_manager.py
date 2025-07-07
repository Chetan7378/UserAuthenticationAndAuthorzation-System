import logging 
from typing import List, Optional 
from models.user_models import UserInfo 
from security.authentication.auth_strategy import IAuthStrategy 
from security.user_management.user_manager import IUserManager 
from exceptions.custom_exceptions import InvalidCredentialsError
from constants.error_messages import ErrorMessages
logger = logging.getLogger(__name__)

class LdapManager: 
    """Manager for LDAP authentication and user management operations."""
    def init(self, auth_strategy: IAuthStrategy, user_manager: IUserManager): 
        self.auth_strategy = auth_strategy 
        self.user_manager = user_manager

    async def authenticate_user(self, username: str, password: str) -> UserInfo:
        """Authenticates a user using the configured strategy."""
        logger.info(f"Attempting to authenticate user: {username}")
        user_info = await self.auth_strategy.authenticate(username, password)
        
        if not user_info:
            raise InvalidCredentialsError()
        logger.info(f"User {username} authenticated successfully.")
        return user_info

    async def get_user_details(self, username: str) -> Optional[UserInfo]:
        """Retrieves user details."""
        logger.info(f"Fetching details for user: {username}")
        return await self.user_manager.get_user_details(username)

    async def get_all_users_in_group(self, group_name: str) -> List[UserInfo]:
        """Retrieves all users within a specified group."""
        logger.info(f"Fetching all users in group: {group_name}")
        return await self.user_manager.get_all_users_in_group(group_name)

    async def check_user_group_membership(self, group_name: str, username: str) -> bool:
        """Checks if a user is a member of a specific group."""
        logger.info(f"Checking group membership for {username} in {group_name}")
        return await self.user_manager.check_group_membership(group_name, username)