from typing import Any

__all__ = [
    "dict_first_val",
]


def dict_first_val(x: dict) -> Any:
    return tuple(x.values())[0]
