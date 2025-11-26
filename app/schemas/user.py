import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    tier: str | None = "free"


class UserLogin(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    avatar_url: str | None = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters long")
        
# Properties to return to client
class UserResponse(UserBase):
    id: uuid.UUID
    tier: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

class UserAdminUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    tier: str | None = None
    email_verified: bool | None = None
    full_name: str | None = None