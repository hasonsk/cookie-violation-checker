from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.repositories.user_repository import UserRepository
from src.schemas.user import User, UserRole
from src.dependencies.dependencies import get_current_admin_user
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
