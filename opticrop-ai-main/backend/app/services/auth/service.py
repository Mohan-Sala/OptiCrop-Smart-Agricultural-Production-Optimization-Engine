import logging
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from app.core.security import get_password_hash, verify_password
from app.core.roles import UserRole
from app.models.user import User
from app.models.login_audit import LoginAudit
from app.models.user_setting import UserSetting
from app.repositories.interfaces.user import UserRepository
from app.repositories.interfaces.login_audit import LoginAuditRepository
from app.utils.exceptions import AuthenticationException, ValidationException

logger = logging.getLogger("app.services.auth")


class AuthService:
    """Orchestrates authentication workflow, registrations, logins, resets, and audit logs."""

    def __init__(self, user_repo: UserRepository, audit_repo: LoginAuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    def hash_reset_token(self, token: str) -> str:
        """Computes SHA-256 hash of a password reset token."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def register_user(
        self, email: str, password: str, full_name: str, role: UserRole = UserRole.FARMER
    ) -> User:
        """Registers a new User profile, automatically adding baseline user settings."""
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValidationException("Email address already registered.")

        hashed_pwd = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_pwd,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        # ORM cascade inserts UserSetting automatically
        new_user.settings.append(UserSetting(theme="system", language="en"))

        user = await self.user_repo.create(new_user)
        logger.info("Successfully registered user profile: %s (Role: %s)", email, role)
        return user

    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_name: Optional[str] = None,
    ) -> User:
        """Authenticates user credentials, writing audit entries to DB on success or failure."""
        user = await self.user_repo.get_by_email(email)

        if not user:
            # Audit failed login attempt (Unknown User)
            await self.audit_repo.create(
                LoginAudit(
                    user_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_name=device_name,
                    success=False,
                    failure_reason="User profile not found",
                )
            )
            logger.warning("Authentication failed: Unknown email address %s", email)
            raise AuthenticationException("Authentication failed: invalid email or password.")

        if not user.is_active:
            await self.audit_repo.create(
                LoginAudit(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_name=device_name,
                    success=False,
                    failure_reason="User account is deactivated",
                )
            )
            logger.warning("Authentication failed: Deactivated user attempt %s", email)
            raise AuthenticationException("Access denied: user account is deactivated.")

        if not verify_password(password, user.hashed_password):
            await self.audit_repo.create(
                LoginAudit(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_name=device_name,
                    success=False,
                    failure_reason="Incorrect credentials",
                )
            )
            logger.warning("Authentication failed: Incorrect password attempt for %s", email)
            raise AuthenticationException("Authentication failed: invalid email or password.")

        # Log successful authentication
        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update(user.id, {"last_login": user.last_login})

        await self.audit_repo.create(
            LoginAudit(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                device_name=device_name,
                success=True,
            )
        )
        logger.info("Authentication succeeded: User session active for %s", email)
        return user

    async def initiate_password_reset(self, email: str) -> str:
        """Generates password reset tokens and stores verification hashes."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Prevent user enumeration attacks by returning a mock token value
            return secrets.token_urlsafe(32)

        raw_token = secrets.token_urlsafe(32)
        token_hash = self.hash_reset_token(raw_token)
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)

        await self.user_repo.update(
            user.id, {"reset_token_hash": token_hash, "reset_token_expiry": expiry}
        )
        logger.info("Initiated password reset workflow for user: %s", email)
        return raw_token

    async def complete_password_reset(self, token: str, new_password: str) -> None:
        """Completes password resets by comparing SHA-256 token hashes."""
        token_hash = self.hash_reset_token(token)

        # Retrieve user by token hash
        user = await self.user_repo.get_by_reset_token_hash(token_hash)
        if not user:
            raise ValidationException("Invalid or expired password reset token.")

        if user.reset_token_expiry < datetime.now(timezone.utc):
            raise ValidationException("Invalid or expired password reset token.")

        hashed_pwd = get_password_hash(new_password)
        await self.user_repo.update(
            user.id,
            {
                "hashed_password": hashed_pwd,
                "reset_token_hash": None,
                "reset_token_expiry": None,
            },
        )
        logger.info("Password reset successfully completed for user: %s", user.email)
