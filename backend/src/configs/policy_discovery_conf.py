import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BROWSER_TIMEOUT = int(os.environ.get("BROWSER_TIMEOUT", "30"))
USER_AGENT = os.environ.get("USER_AGENT")

COOKIE_POLICY_PATTERNS = [
    # English patterns
    r'cookie[s]?\s*policy',
    r'cookie[s]?\s*notice',
    r'cookie[s]?\s*statement',
    r'cookie[s]?\s*information',
    r'cookie[s]?\s*settings',
    r'use\s*of\s*cookie[s]?',

    # Vietnamese patterns
    r'chính\s*sách\s*cookie[s]?',
    r'thông\s*báo\s*cookie[s]?',
    r'sử\s*dụng\s*cookie[s]?',
    r'quy\s*định\s*cookie[s]?',

    # Other languages
    r'política\s*de\s*cookie[s]?',  # Spanish/Portuguese
    r'politique\s*de\s*cookie[s]?',  # French
    r'cookie[s]?\s*richtlinie',  # German
    r'informativa\s*cookie[s]?',  # Italian
]

# URL patterns
URL_PATTERNS = [
    r'/cookie[s]?[-_]?policy',
    r'/cookie[s]?[-_]?notice',
    r'/privacy.*cookie',
    r'/legal.*cookie',
    r'/cookie[s]?$',
]
# Section selectors
FOOTER_SELECTORS = ['footer', '.footer', '.site-footer']
NAV_SELECTORS = ['nav', '.navigation', '.nav', '.menu']
