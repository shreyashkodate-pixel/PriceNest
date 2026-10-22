"""
PriceNest — Authentication & Account Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.user import (
    TokenResponseData,
    UserLoginRequest,
    UserProfileData,
    UserRegisterRequest,
)
from backend.app.services.auth_service import auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & User Accounts"])


@router.post(
    "/register",
    response_model=StandardResponse[UserProfileData],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[UserProfileData]:
    user_data = await auth_service.register_user(db, payload)
    return StandardResponse(data=user_data)


@router.post(
    "/login",
    response_model=StandardResponse[TokenResponseData],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT access token",
)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponseData]:
    token_data = await auth_service.authenticate_user(db, payload.email, payload.password)
    return StandardResponse(data=token_data)


@router.get(
    "/me",
    response_model=StandardResponse[UserProfileData],
    status_code=status.HTTP_200_OK,
    summary="Retrieve authenticated user profile",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> StandardResponse[UserProfileData]:
    return StandardResponse(
        data=UserProfileData(
            user_id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
        )
    )
