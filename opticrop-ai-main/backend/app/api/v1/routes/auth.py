from datetime import timedelta
from fastapi import APIRouter, Depends, Request, status

from app.core.config import settings
from app.dependencies.auth import (
    get_user_repository,
    get_refresh_token_repository,
    get_login_audit_repository,
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfileResponse,
)
from app.services.auth import AuthService, TokenService, create_token
from app.utils.responses import success_response, error_response

router = APIRouter()


def get_auth_service(
    user_repo=Depends(get_user_repository),
    audit_repo=Depends(get_login_audit_repository),
) -> AuthService:
    return AuthService(user_repo, audit_repo)


def get_token_service(
    token_repo=Depends(get_refresh_token_repository),
) -> TokenService:
    return TokenService(token_repo)


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Registers a new User profile."""
    user = await auth_service.register_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    token_service: TokenService = Depends(get_token_service),
):
    """Authenticates credentials and registers a device login session."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Authenticate credentials (creates LoginAudit entries internally)
    user = await auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
        user_agent=user_agent,
        device_name=payload.device_name,
    )

    # Generate Access Token
    access_token_expires = timedelta(minutes=15)
    access_token = create_token(
        data={"sub": str(user.id), "type": "access"},
        expires_delta=access_token_expires,
    )

    # Generate Hashed Refresh Token
    refresh_token = await token_service.create_refresh_token(
        user_id=user.id,
        device_name=payload.device_name,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
        user=user,
    )


@router.post("/logout")
async def logout(
    payload: TokenRefreshRequest,
    token_service: TokenService = Depends(get_token_service),
):
    """Revokes the active refresh token session (device logout)."""
    revoked = await token_service.revoke_refresh_token(payload.refresh_token)
    if not revoked:
        return error_response(message="Session logout failed: token not found or already inactive.")
    return success_response(message="Session logged out successfully.")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    payload: TokenRefreshRequest,
    user_repo=Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
):
    """Rotates refresh tokens and issues fresh access tokens."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Verifies the used token and generates a new rotated one
    new_refresh_token, user_id_str = await token_service.verify_and_rotate_refresh_token(
        payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    user = await user_repo.get_by_id(user_id_str)

    access_token_expires = timedelta(minutes=15)
    new_access_token = create_token(
        data={"sub": str(user_id_str), "type": "access"},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
        user=user,
    )


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Initiates the password reset workflow, returning a token."""
    raw_token = await auth_service.initiate_password_reset(payload.email)
    # Note: In production, this raw_token would be sent to the user's email address.
    # For Phase 3 implementation, we return it in the JSON response payload.
    return success_response(
        message="Reset instructions generated.",
        data={"reset_token": raw_token},
    )


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Completes the password reset workflow using a token."""
    await auth_service.complete_password_reset(
        token=payload.token,
        new_password=payload.new_password,
    )
    return success_response(message="Password has been successfully updated.")
