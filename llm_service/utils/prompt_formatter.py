from typing import Any

class PromptFormatter:
    ALPACA_PROMPT = """You are an expert AI assistant specialized in analyzing website cookie policies. Your task is to read the provided cookie policy text and extract detailed, structured information about each cookie mentioned, adhering strictly to the guidelines and format specified below.
RESPONSE Format: JSON following structure:

{{
  "is_specific": 0,
  "cookies": [
     {{
      "cookie_name": "cookie_name",
      "declared_purpose": "declared_purpose",
      "declared_retention": "declared_retention",
      "declared_third_parties": ["declared_third_parties"],
      "declared_description": "declared_description"
    }}, ...
  ]
}}
If no cookies are specifically described, only response {{"is_specific": 0, "cookies": []}}

### Instruction:
{}

### Input:
{}

### Response:
"""

    SYSTEM_PROMPT = """
Extraction guidelines:
For "is_specific": Determines if the website provides detailed descriptions of individual cookies:
- Set to 0 if cookies are only described generically (e.g., "performance cookies," "necessary cookies," "Google cookies") without specific explanations
- Set to 1 if cookies are described with specific names, purposes, retention periods, and third parties. Example: "The '_ga' cookie is used by Google Analytics to distinguish users and is stored for 2 years" would result in is_specific = 1

For the "cookies" list containing objects, each object has
- "cookie_name": Extract the exact technical name as mentioned. One object just has only one cookie name, ìf more one, create multiple objects. For example: ga, _gid, _gat --> 3 object cookies
- "declared_purpose": cookie's purpose. With the following options:
  * Strictly Necessary: Essential for basic website functionality
  * Functionality: Personalizes user experience
  * Analytical: Collects usage data
  * Targeting/Advertising/Marketing: For personalized ads
  * Performance: Improves technical performance
  * Social Sharing: Enables social media integration
  * Null: When no specific purpose information is provided
- "declared_retention": Record the exact storage duration as mentioned
- "declared_third_parties": An list of third parties involved in the use of this cookie for website-owned cookies
- "declared_description": exact wording from the policy without modification or embellishment

EXTRACT detailed information about each cookie mentioned in that policy"""

    @classmethod
    def format_prompt(cls, content: str, tokenizer: Any) -> str:
        eos_token = tokenizer.eos_token
        instruction = cls.SYSTEM_PROMPT
        input_text = content

        formatted_prompt = cls.ALPACA_PROMPT.format(instruction, input_text) + eos_token
        return formatted_prompt

    @classmethod
    def extract_response(cls, generated_text: str) -> str:
        if "assistant" in generated_text:
            result_text = generated_text.split("assistant")[-1].strip()
        else:
            if "### Response:" in generated_text:
                result_text = generated_text.split("### Response:")[-1].strip()
            else:
                result_text = generated_text.strip()

        return result_text
