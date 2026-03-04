from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_token_pair, decode_token
from app.exceptions import AuthenticationError, ValidationError
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegister) -> TokenResponse:
        # Check existing user
        result = await self.db.execute(
            select(User).where(
                or_(User.email == data.email, User.username == data.username)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if existing.email == data.email:
                raise ValidationError("Email already registered")
            raise ValidationError("Username already taken")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        access_token, refresh_token = create_token_pair(user.id, user.username)

        logger.info("user_registered", user_id=user.id, username=user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: UserLogin) -> TokenResponse:
        result = await self.db.execute(
            select(User).where(
                or_(User.email == data.username, User.username == data.username)
            )
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        user.last_login = datetime.utcnow()
        await self.db.flush()

        access_token, refresh_token = create_token_pair(user.id, user.username)

        logger.info("user_login", user_id=user.id, username=user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        access_token, new_refresh = create_token_pair(user.id, user.username)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def change_password(self, user: User, current_password: str, new_password: str):
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.db.flush()

        logger.info("password_changed", user_id=user.id)
        return {"message": "Password changed successfully"}