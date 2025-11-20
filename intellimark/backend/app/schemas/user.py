from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# -------- Core User Schemas --------

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    is_admin: bool = False


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithOrganization(UserResponse):
    organization_name: Optional[str] = None


# -------- Activity Log Schemas --------

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    timestamp: datetime

    class Config:
        from_attributes = True
