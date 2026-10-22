"""
PriceNest — User Authentication & Authorization Service
"""

from typing import Optional

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.exceptions import AuthenticationError, ConflictError
from backend.app.core.logging import logger
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.app.models.user import User
from backend.app.schemas.user import (
    TokenResponseData,
    UserProfileData,
    UserRegisterRequest,
)


class AuthService:
    """Handles user registration, authentication, and JWT lifecycle."""

    async def register_user(
        self, db: AsyncSession, payload: UserRegisterRequest
    ) -> UserProfileData:
        # Check if email is already registered
        query = select(User).where(User.email == payload.email.lower().strip())
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictError(f"Account with email '{payload.email}' already exists.")

        # Hash password and create record
        hashed_pwd = hash_password(payload.password)
        new_user = User(
            email=payload.email.lower().strip(),
            hashed_password=hashed_pwd,
            full_name=payload.full_name,
            is_active=True,
        )
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)

        logger.info(f"Registered new user account: {new_user.email} (ID: {new_user.id})")
        return UserProfileData(
            user_id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
        )

    async def authenticate_user(
        self, db: AsyncSession, email: str, password: str
    ) -> TokenResponseData:
        query = select(User).where(User.email == email.lower().strip())
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication attempt for email: {email}")
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("User account is inactive.")

        token = create_access_token(
            subject=user.id,
            claims={"email": user.email, "name": user.full_name},
        )
        logger.info(f"User {user.email} logged in successfully.")
        return TokenResponseData(
            access_token=token,
            token_type="bearer",
            expires_in=86400,  # 24 hours in seconds
        )

    async def get_user_by_id(
        self, db: AsyncSession, user_id: str
    ) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()


auth_service = AuthService()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency enforcing that the caller must supply a valid Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or malformed Authorization header.")

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload missing subject identifier.")

    user = await auth_service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User associated with token not found or inactive.")

    return user


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Dependency that extracts user if Bearer token present, else returns None (guest)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await auth_service.get_user_by_id(db, user_id)
    except Exception:
        return None
