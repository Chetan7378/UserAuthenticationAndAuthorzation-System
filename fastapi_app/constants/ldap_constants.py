# src/constants/ldap_constants.py
from enum import Enum

class LdapConstants(str, Enum):
    """Constants for LDAP operations."""
    OBJECT_CLASS_GROUP = "groupOfNames"
    OBJECT_CLASS_ANY = "*"
    MEMBER_ATTRIBUTE = "member"
    CN_ATTRIBUTE = "cn"
    MAIL_ATTRIBUTE = "mail"
    SN_ATTRIBUTE = "sn"
    UID_ATTRIBUTE = "uid"

class LdapAttributes(str, Enum):
    CN = "cn"
    MAIL = "mail"
    SN = "sn"
    UID = "uid"