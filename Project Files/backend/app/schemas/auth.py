import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.core.roles import UserRole


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Unique email address for user registration")
    password: str = Field(..., description="Plaintext password meeting strength requirements")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of user")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Plaintext password")
    device_name: Optional[str] = Field(None, description="Optional name of authenticating device")


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    bio: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT short-lived access token")
    refresh_token: str = Field(..., description="Rotatable database-persisted refresh token")
    token_type: str = Field("bearer", description="Token transport type")
    expires_in: int = Field(3600, description="Access token lifetime in seconds")
    user: UserProfileResponse = Field(..., description="Serialized profile of authenticated user")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Raw refresh token value")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Account email to dispatch reset token to")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Raw reset token received")
    new_password: str = Field(..., description="New plaintext password to set")
