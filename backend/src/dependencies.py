from fastapi import Depends
from pymongo.collection import Collection
from repositories.user_repository import UserRepository
from services.auth_service.auth_service import AuthService
from configs.database import get_collection
from configs.app_settings import USERS_COLLECTION

def get_user_repository(
    users_collection: Collection = Depends(lambda: get_collection(USERS_COLLECTION))
) -> UserRepository:
    return UserRepository(users_collection)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repo)
