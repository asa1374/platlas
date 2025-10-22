from __future__ import annotations

import re
import unicodedata


def slugify(value: str) -> str:
    """Create a URL-friendly slug from a string."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
    normalized = re.sub(r"[\s_-]+", "-", normalized).strip("-")
    return normalized or "platform"
