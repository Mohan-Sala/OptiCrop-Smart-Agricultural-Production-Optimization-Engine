from typing import Optional
from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=255)
    occupation: Optional[str] = Field(None, max_length=255)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="Current plaintext password")
    new_password: str = Field(..., description="New secure plaintext password")
