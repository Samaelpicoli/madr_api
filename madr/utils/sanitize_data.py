import re


def sanitize_text_in(text: str) -> str:
    sanitized = text.lower()
    sanitized = sanitized.strip()
    sanitized = re.sub(r'[?!]', '', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized


def sanitize_text_out(text: str) -> str:
    sanitized = text.strip()
    sanitized = re.sub(r'\s+', ' ', sanitized)
    sanitized = sanitized.title()
    return sanitized
