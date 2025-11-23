import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    tier: str | None = "free"  # Add tier with default "free"

class UserLogin(UserBase):
    password: str
        
# Properties to return to client
class UserResponse(UserBase):
    id: uuid.UUID
    tier: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)