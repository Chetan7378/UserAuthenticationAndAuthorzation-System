# src/models/user_models.py
from pydantic import BaseModel, Field
from typing import Optional

class UserInfo(BaseModel):
    """Pydantic model for user information."""
    cn: Optional[str] = Field(None, description="Common Name")
    mail: Optional[str] = Field(None, description="Email Address")
    sn: Optional[str] = Field(None, description="Surname")
    uid: Optional[str] = Field(None, description="User ID")