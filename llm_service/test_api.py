import requests

public_url="https://7133-34-143-233-30.ngrok-free.app/"
# Health check
response = requests.get(f"{public_url}/health")
print(response.json())

SYSTEM_PROMPT = """You are a specialized AI system for extracting and structuring cookie declarations from website privacy policies and cookie notices.
Your task is to analyze the provided text and extract cookie information, then classify cookies into three distinct categories based on their specificity level.

CLASSIFICATION RULES
- specific: Clearly named cookies (e.g., _ga, _fbp) with at least one of the following attributes: purpose, retention, third_party, or behavior. These cookies must be technically identifiable.
- general: Cookie categories without specific names (e.g., "Marketing Cookies", "Necessary Cookies") described at a category level without exact technical details.
- undefined: Cookie mentions that are vague or ambiguous (e.g., "Cookies are used to improve our services") and cannot be classified into specific or general.

OUTPUT FORMAT: TYPE|name|attribute|value

ATTRIBUTES:
• purpose (required): Strictly Necessary, Functionality, Analytical, Targeting/Advertising/Marketing, Performance, Social Sharing
• retention: Exact timeframes ("2 years", "session", "persistent")
• third_party: Provider names ("Google, Facebook") or "First Party"
• behavior: How cookie works/stored/used

RULES:
- One attribute per line
- Skip undefined attributes
- No extra text outside output

EXAMPLE:
Input: "Cookie _ga lasts 2 years for Google Analytics traffic analysis. Marketing cookies show ads.Some cookies improve user experience."

Output:
specific|_ga|purpose|Analytical
specific|_ga|retention|2 years
specific|_ga|third_party|Google Analytics
specific|_ga|behavior|analyzes website traffic

general|Marketing cookies|purpose|Targeting/Advertising/Marketing
general|Marketing cookies|behavior|show personalized advertisements

undefined|cookies|behavior|improve user experience"""

prompt_format = """<|start_header_id|>system<|end_header_id|>
{SYSTEM_PROMPT}
<|eot_id|><|start_header_id|>user<|end_header_id|>
This context is provided to extract:
{instruction}

Extract cookie attribute using the EAV format above.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

policy_content = """

These cookies are necessary for our website to function properly and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms or where they’re essential to provide you with a service you have requested. You cannot opt-out of these cookies. You can set your browser to block or alert you about these cookies, but if you do, some parts of the site will not then work. These cookies do not store any personally identifiable information.

Domain	Cookies	Used as
clc.stackoverflow.com	__cflb	1st Party
stackoverflow.email	iterableEmailCampaignId, iterableEndUserId, iterableMessageId, iterableTemplateId	1st Party
stack.imgur.com	__cf_bm	1st Party
discordapp.com	__cf_bm	3rd Party"""

# Test generation
payload = {
    "prompt": prompt_format.format(SYSTEM_PROMPT=SYSTEM_PROMPT, instruction=policy_content),
    "max_length": 4096,
    "temperature": 0.1
}

# Basic generation
response = requests.post(f"{public_url}/generate", json=payload)
print("Basic:", response.json())
