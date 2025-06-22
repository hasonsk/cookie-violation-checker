from src.configs.settings import settings

class PromptBuilder:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt

    def build_cookie_extraction_prompt(self, content_to_analyze: str) -> str:
        """
        Builds the prompt for extracting cookie features.
        """
        return f"{self.system_prompt}\n\nContent to analyze:\n{content_to_analyze}"
