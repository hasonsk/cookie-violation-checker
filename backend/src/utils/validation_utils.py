import re
from typing import Annotated
from pydantic import BeforeValidator

DOMAIN_REGEX = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"

def validate_domain_format(domain: str) -> str:
    if not re.match(DOMAIN_REGEX, domain):
        raise ValueError(f"Invalid domain format: {domain}")
    return domain

DomainString = Annotated[str, BeforeValidator(validate_domain_format)]
