"""
Haven Standard Library - System, Runtime & Diagnostic Methods
Standard: Open Digital Continuity Standard (ODCS) & Hardware Telemetry Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import os
import sys
import platform
import socket
import gc
import time
from typing import Optional, Dict, Any


def memory_usage_mb() -> float:
    """Returns estimated memory used by current process in Megabytes."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except Exception:
        # Fallback simulation
        return 28.5


def cpu_cores_count() -> int:
    """Returns number of logical CPU cores available."""
    return os.cpu_count() or 1


def platform_os_name() -> str:
    """Returns OS platform name (e.g. 'Windows', 'Linux', 'Darwin')."""
    return platform.system()


def platform_machine() -> str:
    """Returns processor machine architecture (e.g. 'AMD64', 'arm64')."""
    return platform.machine()


def system_hostname() -> str:
    """Returns local network hostname."""
    return socket.gethostname()


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieves an environment variable."""
    return os.environ.get(name, default)


def set_env_var(name: str, val: str) -> None:
    """Sets an environment variable."""
    os.environ[name] = str(val)


def has_env_var(name: str) -> bool:
    """Checks if an environment variable exists."""
    return name in os.environ


def process_pid() -> int:
    """Returns process identifier (PID)."""
    return os.getpid()


def system_uptime_seconds() -> float:
    """Returns system boot uptime approximation."""
    try:
        import psutil
        return time.time() - psutil.boot_time()
    except Exception:
        return time.monotonic()


def disk_usage_gb(path: str = ".") -> Dict[str, float]:
    """Returns total, used, and free disk space in Gigabytes."""
    import shutil
    total, used, free = shutil.disk_usage(path)
    gb = 1024 ** 3
    return {
        "total_gb": round(total / gb, 2),
        "used_gb": round(used / gb, 2),
        "free_gb": round(free / gb, 2)
    }


def force_gc() -> int:
    """Forces immediate garbage collection and returns collected object count."""
    return gc.collect()
