import re

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def ensure_devanagari_text(text: str) -> str:
    clean_text = (text or "").strip()
    if not clean_text:
        raise ValueError("Text cannot be empty")

    if _LATIN_RE.search(clean_text):
        raise ValueError("Only Devanagari (Nepali) text is allowed")

    if not _DEVANAGARI_RE.search(clean_text):
        raise ValueError("Text must contain Devanagari (Nepali) characters")

    return clean_text
