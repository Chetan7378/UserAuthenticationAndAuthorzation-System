# src/security/user_management/ldap_user_manager.py
import logging
import asyncio
from typing import List
from ldap3 import Connection
from config.ldap_config import LdapConfig
from models.user_models import UserInfo
from security.user_management.user_manager import IUserManager
from security.connection.ldap_connection_manager import LdapConnectionManager
from exceptions.custom_exceptions import LDAPAuthError, GroupNotFound, InputValidationError, LDAPBindError
from constants.error_messages import ErrorMessages
from constants.ldap_constants import LdapAttributes, LdapConstants

logger = logging.getLogger(__name__)

class LdapUserManager(IUserManager):
    """LDAP specific implementation of IUserManager."""
    def __init__(self, config: LdapConfig, conn_manager: LdapConnectionManager):
        self.base_dn = config.LDAP_BASE_DN
        self.group_dn = config.LDAP_GROUP_DN
        self.conn_manager = conn_manager

    async def get_user_details(self, username: str) -> UserInfo:
        """Retrieves user details from LDAP."""
        return await asyncio.to_thread(self._get_user_details_sync, username)

    def _get_user_details_sync(self, username: str) -> UserInfo:
        conn: Connection = None
        try:
            conn = self.conn_manager.connect()
            entries = self.conn_manager.search(
                conn, self.base_dn, f'({LdapAttributes.CN}={username})',
                [LdapAttributes.CN, LdapAttributes.MAIL, LdapAttributes.SN, LdapAttributes.UID]
            )
            if not entries:
                logger.warning(f"User {username} not found in LDAP.")
                return None # Or raise a specific UserNotFound exception

            entry = entries[0]
            return UserInfo(
                cn=getattr(entry, LdapAttributes.CN.value, None).value,
                mail=getattr(entry, LdapAttributes.MAIL.value, None).value,
                sn=getattr(entry, LdapAttributes.SN.value, None).value,
                uid=getattr(entry, LdapAttributes.UID.value, None).value
            )
        except Exception as e:
            logger.exception(f"Error fetching user details for {username}: {e}")
            raise LDAPAuthError(detail=ErrorMessages.UNEXPECTED_ERROR)
        finally:
            self.conn_manager.disconnect(conn)

    async def get_all_users_in_group(self, group_name: str) -> List[UserInfo]:
        """Retrieves all users in a given LDAP group."""
        return await asyncio.to_thread(self._get_all_users_in_group_sync, group_name)

    def _get_all_users_in_group_sync(self, group_name: str) -> List[UserInfo]:
        users = []
        conn: Connection = None
        try:
            conn = self.conn_manager.connect()
            group_filter = f"(&({LdapConstants.OBJECT_CLASS_GROUP})({LdapAttributes.CN}={group_name}))"
            group_entries = self.conn_manager.search(
                conn, self.group_dn, group_filter, [LdapConstants.MEMBER_ATTRIBUTE]
            )

            if not group_entries:
                logger.warning(f"Group '{group_name}' not found or has no members.")
                raise GroupNotFound(detail=ErrorMessages.GROUP_NOT_FOUND)

            for group_entry in group_entries:
                member_dns = getattr(group_entry, LdapConstants.MEMBER_ATTRIBUTE.value, [])
                if not member_dns:
                    continue # Group found but no members listed

                for member_dn in member_dns:
                    user_entries = self.conn_manager.search(
                        conn, member_dn, f'({LdapConstants.OBJECT_CLASS_ANY})',
                        [LdapAttributes.CN, LdapAttributes.MAIL, LdapAttributes.SN, LdapAttributes.UID]
                    )
                    if user_entries:
                        info = user_entries[0]
                        users.append(UserInfo(
                            cn=getattr(info, LdapAttributes.CN.value, None).value,
                            mail=getattr(info, LdapAttributes.MAIL.value, None).value,
                            sn=getattr(info, LdapAttributes.SN.value, None).value,
                            uid=getattr(info, LdapAttributes.UID.value, None).value
                        ))
            return [user for user in users if any(getattr(user, attr) for attr in UserInfo.model_fields.keys())]
        except GroupNotFound:
            raise        
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_users_in_group for '{group_name}': {e}")
            raise LDAPAuthError(detail=ErrorMessages.UNEXPECTED_ERROR)
        finally:
            self.conn_manager.disconnect(conn)

    async def check_group_membership(self, group_name: str, username: str) -> bool:
        """Checks if a user is a member of a specific LDAP group."""
        return await asyncio.to_thread(self._check_group_membership_sync, group_name, username)

    def _check_group_membership_sync(self, group_name: str, username: str) -> bool:
        if not group_name or not username:
            raise InputValidationError(detail=ErrorMessages.MISSING_INPUT)

        conn: Connection = None
        try:
            conn = self.conn_manager.connect()
            user_dn = f"{LdapAttributes.CN}={username},{self.base_dn}"
            search_filter = (
                f"(&({LdapConstants.OBJECT_CLASS_GROUP})"
                f"({LdapAttributes.CN}={group_name})"
                f"({LdapConstants.MEMBER_ATTRIBUTE}={user_dn}))"
            )
            entries = self.conn_manager.search(conn, self.group_dn, search_filter, [LdapAttributes.CN])

            is_member = bool(entries)
            logger.info(f"User {username} {'IS' if is_member else 'IS NOT'} a member of group {group_name}.")
            return is_member
        except LDAPBindError:
            raise # Re-raise if connection failed
        except Exception as e:
            logger.exception(f"LDAP group membership check failed for {username} in {group_name}: {e}")
            raise LDAPAuthError(detail=ErrorMessages.MEMBERSHIP_CHECK_FAILED)        
        finally:
            self.conn_manager.disconnect(conn)