import difflib

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts"""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def infer_cookie_purpose(cookie_name: str, cookie_value: str, domain: str) -> str:
    """Infer cookie purpose based on analysis"""
    name_lower = cookie_name.lower()
    value_lower = cookie_value.lower() if cookie_value else ""
    domain = domain.lower()

    # Pattern groups with purposes
    pattern_groups = [
        ([r'session', r'auth', r'login', r'token', r'csrf', r'user[_-]?id', r'account', r'remember'],
         "Authentication/Session Management"),
        ([r'analytics?', r'ga[0-9]?', r'gtm', r'track', r'pixel', r'_utm', r'campaign', r'source', r'medium'],
         "Analytics/Tracking"),
        ([r'ad[sv]?', r'marketing', r'retarget', r'audience', r'conversion', r'attribution', r'affiliate'],
         "Advertising/Marketing"),
        ([r'preference', r'setting', r'language', r'currency', r'theme', r'layout', r'cart', r'wishlist'],
         "Functional/Preferences"),
        ([r'performance', r'speed', r'load', r'cache', r'cdn', r'optimization'],
         "Performance/Optimization")
    ]

    for patterns, purpose in pattern_groups:
        for pattern in patterns:
            if (re.search(pattern, name_lower) or re.search(pattern, value_lower)):
                return purpose

    return "Unknown/Unclassified"
