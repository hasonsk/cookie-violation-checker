import logging
from typing import List

TIMEOUT = 30
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Cookie policy patterns
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

# Selectors for finding policy links
POLICY_SELECTORS = [
    # Footer selectors
    'footer a[href*="cookie"]',
    'footer a[href*="privacy"]',
    '.footer a[href*="cookie"]',
    '.site-footer a[href*="cookie"]',

    # Navigation selectors
    'nav a[href*="cookie"]',
    '.navigation a[href*="cookie"]',
    '.nav a[href*="cookie"]',

    # Generic link selectors
    'a[href*="cookie-policy"]',
    'a[href*="cookies-policy"]',
    'a[href*="cookie_policy"]',
    'a[href*="cookies_policy"]',

    # Link tag selectors
    'link[rel*="policy"]',
    'link[href*="cookie"]',
]

# Section selectors
FOOTER_SELECTORS = ['footer', '.footer', '.site-footer']
NAV_SELECTORS = ['nav', '.navigation', '.nav', '.menu']
