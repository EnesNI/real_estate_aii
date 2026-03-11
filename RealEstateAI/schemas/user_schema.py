from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for user registration."""

    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=64)


class UserLogin(BaseModel):
    """Payload for user login."""

    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6, max_length=64)


class UserOut(BaseModel):
    """Public user profile information."""

    id: int
    username: str
    email: EmailStr
    created_at: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Login response containing a token and user profile."""

    token: str
    user: UserOut


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str


class UserProfile(BaseModel):
    """User profile summary with prediction counts."""

    user: UserOut
    prediction_count: int
