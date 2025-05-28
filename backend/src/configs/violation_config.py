from pydantic import BaseSettings

class ViolationAnalysisSettings(BaseSettings):
    """Settings for violation analysis service"""

    # Analysis thresholds
    RETENTION_THRESHOLD_PERCENTAGE: float = 30.0
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.5
    LONG_TERM_RETENTION_DAYS: int = 365
    SESSION_THRESHOLD_HOURS: int = 24

    # Scoring
    ISSUE_PENALTY_POINTS: int = 5
    MAX_COMPLIANCE_SCORE: int = 100

    # Known trackers (can be moved to database)
    KNOWN_AD_TRACKERS: list = [
        'doubleclick.net', 'google-analytics.com', 'facebook.com',
        'twitter.com', 'linkedin.com', 'amazon-adsystem.com'
    ]

    # Purpose labels for semantic analysis
    STANDARD_PURPOSE_LABELS: list = [
        "Strictly Necessary", "Functionality", "Analytical",
        "Targeting/Advertising/Marketing", "Performance", "Social Sharing"
    ]

    class Config:
        env_file = ".env"
        env_prefix = "VIOLATION_"
