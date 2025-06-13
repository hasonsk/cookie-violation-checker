from abc import ABC, abstractmethod
from typing import Optional

class ISearchProvider(ABC):

    @abstractmethod
    async def search_policy(self, domain: str) -> Optional[str]:
        pass
