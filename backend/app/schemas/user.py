"""
PriceNest — User Authentication & Account Pydantic Schemas
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Secure password (minimum 8 characters)",
        examples=["SecurePassword123!"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=128,
        description="User's full name",
        examples=["Pooja Deshmukh"],
    )


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        examples=["SecurePassword123!"],
    )


class TokenResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileData(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
