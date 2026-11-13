"""
Haven Backend Framework - Asynchronous Background Task Queue
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional


class BackgroundTaskPool:
    """Manages concurrent worker threads for asynchronous backend jobs."""
    def __init__(self, max_workers: int = 16):
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="HavenWorker")
        self._is_shutdown = False

    def dispatch(self, func: Callable, *args, **kwargs):
        """Dispatches a function to run asynchronously without blocking response."""
        if not self._is_shutdown:
            return self._executor.submit(func, *args, **kwargs)

    def shutdown(self, wait: bool = False):
        self._is_shutdown = True
        self._executor.shutdown(wait=wait)
