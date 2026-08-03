import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.repositories.interfaces.user import UserRepository
from app.repositories.interfaces.refresh_token import RefreshTokenRepository
from app.repositories.interfaces.login_audit import LoginAuditRepository
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository
from app.repositories.sqlalchemy.refresh_token import SqlAlchemyRefreshTokenRepository
from app.repositories.sqlalchemy.login_audit import SqlAlchemyLoginAuditRepository
from app.services.auth import decode_token
from app.utils.exceptions import AuthenticationException

# Dynamically binds Swagger UI credentials button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# --- Repository Injections ---


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepository(db)


def get_refresh_token_repository(db: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(db)


def get_login_audit_repository(db: AsyncSession = Depends(get_db)) -> LoginAuditRepository:
    return SqlAlchemyLoginAuditRepository(db)


# --- User Context Resolution ---


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Decodes the JWT access token and resolves the matching User model.

    Raises AuthenticationException upon failure.
    """
    if not token:
        raise AuthenticationException("Authentication failed: credentials token missing.")

    payload = decode_token(token)
    user_id_str = payload.get("sub")
    token_type = payload.get("type")

    if not user_id_str or token_type != "access":
        raise AuthenticationException("Authentication failed: invalid token claims.")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationException("Authentication failed: invalid token identifier.")

    user = await user_repo.get_by_id(user_uuid)
    if not user:
        raise AuthenticationException("Authentication failed: user profile not found.")

    return user


async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verifies that the resolved User account is active."""
    if not current_user.is_active:
        raise AuthenticationException("Access denied: user account is deactivated.")
    return current_user
