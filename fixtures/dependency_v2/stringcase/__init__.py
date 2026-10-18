"""Synthetic dependency API v2: rename to_snake -> snake_case."""
import re

__version__ = "2.0.0"


def snake_case(value: str) -> str:
    """Convert spaces and CamelCase-ish input to lowercase underscored text."""
    return re.sub(r"\s+", "_", value.strip()).lower()
