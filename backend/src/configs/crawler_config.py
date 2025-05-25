# Crawler configuration constants
CRAWLER_USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
CRAWLER_TIMEOUT = 50

# Browser configuration
BROWSER_CONFIG = {
    "headless": True,
    "args": ['--no-sandbox', '--disable-dev-shm-usage']
}

BROWSER_CONTEXT_CONFIG = {
    "viewport": {"width": 1280, "height": 800},
    "device_scale_factor": 1,
    "extra_http_headers": {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
}

# Translation settings
TRANSLATION_CONFIG = {
    "max_chunk_size": 4000,
    "rate_limit_delay": 0.1,
    "cache_ttl": 3600 * 24  # 24 hours
}

# Thread pool settings
THREAD_POOL_MAX_WORKERS = 4
