"""Small project broken after upgrading synthetic stringcase to version 2."""
from stringcase import to_snake


def normalize(value: str) -> str:
    return to_snake(value)
