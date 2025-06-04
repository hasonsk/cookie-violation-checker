import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

RETENTION_THRESHOLD_PERCENTAGE = float(os.environ.get("RETENTION_THRESHOLD_PERCENTAGE", "30.0"))
SEMANTIC_SIMILARITY_THRESHOLD = float(os.environ.get("SEMANTIC_SIMILARITY_THRESHOLD", "0.5"))
LONG_TERM_RETENTION_DAYS = int(os.environ.get("LONG_TERM_RETENTION_DAYS", "365"))
SESSION_THRESHOLD_HOURS = int(os.environ.get("SESSION_THRESHOLD_HOURS", "24"))

# Scoring
ISSUE_PENALTY_POINTS: int = 5
MAX_COMPLIANCE_SCORE: int = 100

# Known trackers (can be moved to database)
KNOWN_AD_TRACKERS: list = [
    'doubleclick.net', 'google-analytics.com', 'googletagmanager.com',
    'facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com',
    'amazon-adsystem.com', 'googlesyndication.com', 'adsystem.amazon.com',
    'youtube.com', 'googlevideo.com', 'hotjar.com', 'segment.com',
    'mixpanel.com', 'intercom.io', 'zendesk.com'
]

# Purpose labels for semantic analysis
STANDARD_PURPOSE_LABELS: list = [
"Strictly Necessary", "Functionality", "Analytical",
"Targeting/Advertising/Marketing", "Performance", "Social Sharing"
]
