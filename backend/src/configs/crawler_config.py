import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

USER_AGENT = os.environ.get("USER_AGENT")
CRAWLER_TIMEOUT = os.environ.get("CRAWLER_TIMEOUT")
THREAD_POOL_MAX_WORKERS = int(os.environ.get("THREAD_POOL_MAX_WORKERS"))

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
