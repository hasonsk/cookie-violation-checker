from typing import List, Optional
from datetime import datetime # Import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from src.repositories.user_repository import UserRepository
from src.schemas.user import User, UserRole, UserUpdate
from src.dependencies.dependencies import get_current_admin_user, get_current_user
from src.models.domain_request import DomainRequestStatus
from src.schemas.domain_request import DomainRequestPublic
from src.repositories.domain_request_repository import DomainRequestRepository

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
async def get_users(
    current_role: Optional[UserRole] = None,
    requested_role: Optional[UserRole] = None,
    status: Optional[DomainRequestStatus] = None,
    user_repo: UserRepository = Depends(UserRepository),
    domain_request_repo: DomainRequestRepository = Depends(DomainRequestRepository),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retrieve a list of all users with their basic information, with optional filtering.
    Only accessible by admin users.
    """
    try:
        users_data = await user_repo.get_all_users()
        users_list = []
        for user_data in users_data:
            user_obj = User(**user_data)

            # Apply filters
            if current_role and user_obj.role != current_role:
                continue
            if requested_role and user_obj.requested_role != requested_role:
                continue

            # Fetch domain requests for PROVIDERs and apply status filter
            if user_obj.role == UserRole.PROVIDER:
                domain_requests = await domain_request_repo.get_domain_requests_by_user_id(str(user_obj.id))
                filtered_domain_requests = []
                for dr in domain_requests:
                    if status and dr.status != status:
                        continue
                    filtered_domain_requests.append(
                        DomainRequestPublic(
                            id=str(dr.id),
                            domain=dr.domain,
                            status=dr.status,
                            user_id=str(dr.user_id)
                        )
                    )
                user_obj.domain_requests = filtered_domain_requests
                # If a status filter was applied and no domain requests match, skip this user
                if status and not filtered_domain_requests:
                    continue
            elif status: # If status filter is applied but user is not a PROVIDER, skip
                continue

            users_list.append(user_obj)
        return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading users: {e}"
        )

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the current authenticated user's profile.
    """
    return current_user

@router.patch("/me", response_model=User)
async def update_users_me(
    user_update: UserUpdate,
    user_repo: UserRepository = Depends(UserRepository),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current authenticated user's profile.
    """
    if not user_update.email and not user_update.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (email or name) must be provided for update."
        )

    # Ensure the user cannot change their role or status via this endpoint
    update_data = user_update.model_dump(exclude_unset=True)

    # Prevent updating role or status
    if "role" in update_data:
        del update_data["role"]
    if "status" in update_data:
        del update_data["status"]

    updated_user = await user_repo.update_user(current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Convert ObjectId to str for Pydantic model
    if "_id" in updated_user:
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]

    # Ensure created_at and updated_at are datetime objects
    if "created_at" in updated_user and isinstance(updated_user["created_at"], str):
        updated_user["created_at"] = datetime.fromisoformat(updated_user["created_at"])
    if "updated_at" in updated_user and isinstance(updated_user["updated_at"], str):
        updated_user["updated_at"] = datetime.fromisoformat(updated_user["updated_at"])

    return User(**updated_user)
