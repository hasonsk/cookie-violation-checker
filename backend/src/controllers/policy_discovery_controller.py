from typing import List

from services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService

class PolicyDiscoveryController:

    def __init__(self):
        self.policy_service = PolicyDiscoveryService()

    async def find_single_policy(self, website_url: str) -> dict:
        """Find policy for a single website"""
        async with self.policy_service as finder:
            result = await finder.find_policy_url(website_url)
            return result.to_dict()

    async def find_multiple_policies(self, website_urls: List[str]) -> List[dict]:
        """Find policies for multiple websites"""
        results = []
        async with self.policy_service as finder:
            for url in website_urls:
                result = await finder.find_policy_url(url)
                results.append(result.to_dict())
        return results
