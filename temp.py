from urllib.parse import urlparse

def get_base_url(full_url: str) -> str:
    parsed = urlparse(full_url)
    return f"{parsed.scheme}://{parsed.netloc}"

print(get_base_url("https://chatgpt.com/c/683f7b95-2f9c-8006-907c-4118b7de76d5"))
