"""
Terminal ANSI color utilities for Haven CLI.
"""
import sys
import os

_USE_COLOR = sys.stdout.isatty() or os.environ.get("FORCE_COLOR") == "1"

# Enable VT100 on Windows console if possible
if sys.platform == "win32" and _USE_COLOR:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_out = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h_out, ctypes.byref(mode))
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
    except Exception:
        pass


def color(text: str, code: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return color(text, "1")


def dim(text: str) -> str:
    return color(text, "2")


def green(text: str) -> str:
    return color(text, "32")


def red(text: str) -> str:
    return color(text, "31")


def yellow(text: str) -> str:
    return color(text, "33")


def blue(text: str) -> str:
    return color(text, "34")


def magenta(text: str) -> str:
    return color(text, "35")


def cyan(text: str) -> str:
    return color(text, "36")

