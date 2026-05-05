import re


def is_valid_domain(domain: str) -> bool:
    pattern = re.compile(
        r"^(?:[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,6}$"
    )
    return bool(pattern.match(domain))
