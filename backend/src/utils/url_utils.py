from urllib.parse import urljoin, urlparse

def normalize_url(url: str) -> str:
    """Normalize URL format"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')

def is_absolute_url(url: str) -> bool:
    """Check if URL is absolute"""
    return url.startswith(('http://', 'https://'))

def make_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute"""
    if is_absolute_url(url):
        return url
    return urljoin(base_url, url)

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    return urlparse(url).netloc
