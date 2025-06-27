import torch
from unsloth import FastLanguageModel

class LlamaCookieExtractionService:
    def __init__(self, model_path: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Sử dụng device: {self.device}")
        print("Đang tải mô hình với Unsloth...")

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
        )

        if hasattr(self.model, "eval"):
            self.model.eval()

        self.model.to(self.device)
        print("✅ Mô hình đã sẵn sàng!")

    def build_prompt(self, instruction: str, content: str) -> str:
        return f"""{alpaca_prompt.format(instruction, content)}"""

    def generate_response(self, content: str, max_new_tokens=2048, temperature=0):

        prompt = self.build_prompt(SYSTEM_PROMPT, content)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True,
                                max_length=max_new_tokens).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature,
                top_p=1,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        result_text = decoded_output.split("### Response:")[-1].strip()

        json_start = result_text.find("{")
        json_end = result_text.rfind("}")
        if json_start != -1 and json_end != -1 and json_end > json_start:
            return result_text[json_start:json_end+1]

        return result_text

alpaca_prompt = """You are an expert AI assistant specialized in analyzing website cookie policies. Your task is to read the provided cookie policy text and extract detailed, structured information about each cookie mentioned, adhering strictly to the guidelines and format specified below.
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
