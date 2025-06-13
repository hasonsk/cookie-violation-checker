from abc import ABC, abstractmethod

class IContentExtractor(ABC):

    @abstractmethod
    async def extract_content(self, url: str) -> str:
        """Extract HTML content from URL"""
        pass
