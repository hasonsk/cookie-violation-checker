from typing import Optional
from src.repositories.policy_content_repository import PolicyContentRepository
from src.models.policy import PolicyContent
from src.utils.cache_utils import CacheManager


class PolicyStorageService:
    """Responsible only for storage operations"""

    def __init__(self, repository: PolicyContentRepository, cache_manager: CacheManager):
        self.repository = repository
        self.cache_manager = cache_manager

    async def get_existing_policy(self, root_url: str) -> Optional[PolicyContent]:
        """Get existing policy from storage"""
        return await self.repository.get_by_website_url(root_url)

    async def save_policy(self, web_url: str, policy_content: PolicyContent) -> None:
        """Save policy to both cache and database"""
        await self.cache_manager.cache_content(web_url, policy_content)
        await self.repository.create_policy_content(policy_content.dict(by_alias=True))
