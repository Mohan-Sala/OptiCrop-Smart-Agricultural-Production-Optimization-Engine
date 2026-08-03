from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_active_user, get_user_repository
from app.models.user import User
from app.schemas.auth import UserProfileResponse
from app.schemas.profile import ProfileUpdateRequest, ChangePasswordRequest
from app.services.auth import ProfileService
from app.utils.responses import success_response

router = APIRouter()


def get_profile_service(
    user_repo=Depends(get_user_repository),
) -> ProfileService:
    return ProfileService(user_repo)


@router.get("", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_active_user)):
    """Retrieves the profile of the current active authenticated user."""
    return current_user


@router.put("", response_model=UserProfileResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_active_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Updates user profile properties."""
    # Filter out None values to allow partial updates
    profile_data = payload.model_dump(exclude_unset=True)
    updated_user = await profile_service.update_profile(current_user.id, profile_data)
    return updated_user


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_active_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Updates the user's password."""
    await profile_service.change_password(
        user_id=current_user.id,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    return success_response(message="Password changed successfully.")
