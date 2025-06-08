from typing import List

from src.services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService

class PolicyDiscoveryController:
    def __init__(self, policy_service: PolicyDiscoveryService):
        self.policy_service = policy_service

    async def find_single_policy(self, website_url: str) -> dict:
        result = await self.policy_service.find_policy_url(website_url)
        return result.to_dict()

    async def find_multiple_policies(self, website_urls: List[str]) -> List[dict]:
        results = []
        for url in website_urls:
            result = await self.policy_service.find_policy_url(url)
            results.append(result.to_dict())
        return results
