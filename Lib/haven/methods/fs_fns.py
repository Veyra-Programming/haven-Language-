"""
Haven Standard Library - Filesystem, IO & Path Methods
Standard: Open Digital Continuity Standard (ODCS) & Durable IO Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import os
import shutil
import json
from typing import List, Any, Optional, Dict


def read_text_file(path: str, encoding: str = "utf-8") -> str:
    """Reads complete text content of a file."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_text_file(path: str, content: str, encoding: str = "utf-8") -> int:
    """Writes text content to a file, creating parent directories if needed."""
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding=encoding) as f:
        return f.write(content)


def append_text_file(path: str, content: str, encoding: str = "utf-8") -> int:
    """Appends text content to a file."""
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "a", encoding=encoding) as f:
        return f.write(content)


def read_bytes_file(path: str) -> bytes:
    """Reads raw bytes from a file."""
    with open(path, "rb") as f:
        return f.read()


def write_bytes_file(path: str, data: bytes) -> int:
    """Writes raw bytes to a file."""
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "wb") as f:
        return f.write(data)


def read_json_file(path: str) -> Any:
    """Parses JSON file into a data structure."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path: str, obj: Any, indent: int = 2) -> None:
    """Serializes data structure into a formatted JSON file."""
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent)


def ensure_dir(path: str) -> bool:
    """Recursively creates directory if it does not already exist."""
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        return True
    return False


def file_exists(path: str) -> bool:
    """Checks whether path exists and is a file."""
    return os.path.isfile(path)


def dir_exists(path: str) -> bool:
    """Checks whether path exists and is a directory."""
    return os.path.isdir(path)


def file_size_bytes(path: str) -> int:
    """Returns size of a file in bytes."""
    return os.path.getsize(path)


def list_files_in(dir_path: str, extension: Optional[str] = None) -> List[str]:
    """Lists files in directory, optionally filtered by extension."""
    if not os.path.isdir(dir_path):
        return []
    res = []
    for fn in os.listdir(dir_path):
        fp = os.path.join(dir_path, fn)
        if os.path.isfile(fp):
            if extension is None or fn.endswith(extension):
                res.append(fn)
    return sorted(res)


def list_dirs_in(dir_path: str) -> List[str]:
    """Lists subdirectories within a directory."""
    if not os.path.isdir(dir_path):
        return []
    return sorted([fn for fn in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, fn))])


def copy_file_to(src: str, dst: str) -> str:
    """Copies file from src to dst."""
    ensure_dir(os.path.dirname(os.path.abspath(dst)))
    return shutil.copy2(src, dst)


def move_file_to(src: str, dst: str) -> str:
    """Moves file or directory from src to dst."""
    ensure_dir(os.path.dirname(os.path.abspath(dst)))
    return shutil.move(src, dst)


def remove_file(path: str) -> bool:
    """Deletes a file if it exists."""
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def remove_dir_recursive(path: str) -> bool:
    """Recursively removes a directory tree."""
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


def path_join(*parts: str) -> str:
    """Joins path components using operating system separator."""
    return os.path.join(*parts)


def path_basename(path: str) -> str:
    """Returns the base filename component of a path."""
    return os.path.basename(path)


def path_dirname(path: str) -> str:
    """Returns the directory name component of a path."""
    return os.path.dirname(path)


def path_extension(path: str) -> str:
    """Returns file extension including the leading dot (e.g. '.hvn')."""
    return os.path.splitext(path)[1]


def canonical_path(path: str) -> str:
    """Resolves absolute canonicalized path."""
    return os.path.abspath(path)
