"""Shared API response envelopes (GradVision_API.yaml)."""

from pydantic import BaseModel

from app.schemas.users import User


class SuccessResponse(BaseModel):
    success: bool = True


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


class UserCreateResponse(BaseModel):
    success: bool = True
    user: User
