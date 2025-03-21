from __future__ import annotations

import contextlib
from typing import Protocol

_DEBUG_LEVEL = 0


class DebugPrintFunction(Protocol):
    def __call__(self, __s: str) -> None: ...


def _print_function(s: str):
    print(s)


print_function: DebugPrintFunction = _print_function


def set_level(level: int):
    global _DEBUG_LEVEL
    if isinstance(level, int):
        _DEBUG_LEVEL = level
    else:
        _DEBUG_LEVEL = 0


def debug_level() -> int:
    return _DEBUG_LEVEL


@contextlib.contextmanager
def with_level(level: int):
    current_level = debug_level()
    try:
        set_level(level)
        yield
    finally:
        set_level(current_level)


def debug_print(message: str):
    if _DEBUG_LEVEL > 0:
        print_function(message)
