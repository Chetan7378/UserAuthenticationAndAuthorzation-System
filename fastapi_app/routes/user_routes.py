# src/api/v1/user_routes.py
import logging
from typing import List
from fastapi import APIRouter, Depends, Path, status
from models.user_models import UserInfo
from dependencies.container import get_ldap_manager, verify_access_token
from security.ldap_manager import LdapManager
from security.security_utils import is_safe_ldap_string
from exceptions.custom_exceptions import AuthException, GroupNotFound

router = APIRouter(prefix="/users", tags=["User Management"])
logger = logging.getLogger(__name__)

@router.get("/details", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def get_user_details(
    token_payload: dict = Depends(verify_access_token)
):
   
    user_data = token_payload.get("user")
    if not user_data:
        logger.warning("User info missing in token payload.")
        raise AuthException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User info missing in token")
    logger.info(f"User details requested for {token_payload.get('sub')}.")
    return UserInfo(**user_data)

@router.get("/group-check/{group_name}", status_code=status.HTTP_200_OK)
async def check_user_in_group(
    group_name: str = Path(..., min_length=1, max_length=64),
    token_payload: dict = Depends(verify_access_token),
    ldap_mgr: LdapManager = Depends(get_ldap_manager)
):
    """
    Checks if the authenticated user is a member of a specified LDAP group.
    """
    try:
        is_safe_ldap_string(group_name) # Validate input
        username = token_payload.get("sub")
        if not username:
            raise AuthException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username missing in token.")

        is_member = await ldap_mgr.check_user_group_membership(group_name, username)
        if not is_member:
            logger.warning(f"User {username} is not a member of group {group_name}.")
            raise AuthException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in group.")
        
        logger.info(f"User {username} is a member of group {group_name}.")
        return {"group": group_name, "member": username, "status": "authorized"}
    except AuthException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error checking group membership for {username} in {group_name}: {e}")
        raise AuthException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check group membership.")

@router.get("/group-users/{group_name}", response_model=List[UserInfo], status_code=status.HTTP_200_OK)
async def get_all_users_in_group(
    group_name: str = Path(..., min_length=1, max_length=64),
    token_payload: dict = Depends(verify_access_token), # Requires authentication
    ldap_mgr: LdapManager = Depends(get_ldap_manager)
):
   
    try:
        is_safe_ldap_string(group_name) # Validate input
        # Optional: Add role-based access control here, e.g., only admins can list all users in a group
        # if "admin" not in token_payload.get("roles", []):
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")

        users = await ldap_mgr.get_all_users_in_group(group_name)
        if not users:
            raise GroupNotFound()

        logger.info(f"Retrieved {len(users)} users from group {group_name}.")
        return users
    except AuthException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving users from group {group_name}: {e}")
        raise AuthException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve group users.")
