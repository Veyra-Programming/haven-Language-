"""
Star Language Stack Machine VM & Toolchain Bridge
Specification & Architecture for Star Language & Haven Unified Ecosystem.
"""

import os
import sys
import subprocess
from typing import Any, Dict, List, Optional
from .ui import Widget


class StarApp:
    """Base class for all Star applications (app <Name> ... end)."""
    name: str = "StarApplication"

    def build(self) -> Optional[Widget]:
        return None

    def run(self) -> int:
        root_widget = self.build()
        if root_widget is not None and hasattr(root_widget, "render_tui"):
            print(root_widget.render_tui())
        return 0


class StarVM:
    """Star Stack Machine VM & Execution Manager."""

    @staticmethod
    def find_star_binary() -> Optional[str]:
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Star\bin\star.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Star\bin\star.bat"),
            "star.exe",
            "star",
        ]
        for c in candidates:
            if os.path.isabs(c) and os.path.isfile(c):
                return c
            # Check PATH
            from shutil import which
            found = which(c)
            if found:
                return found
        return None

    @classmethod
    def run_file(cls, filepath: str, *args) -> int:
        bin_path = cls.find_star_binary()
        if bin_path:
            cmd = [bin_path, "run", filepath, *args]
            res = subprocess.run(cmd)
            return res.returncode
        else:
            print(f"[StarVM] Fallback simulated execution: {filepath}")
            return 0

    @classmethod
    def compile_file(cls, filepath: str, *args) -> int:
        bin_path = cls.find_star_binary()
        if bin_path:
            cmd = [bin_path, "compile", filepath, *args]
            res = subprocess.run(cmd)
            return res.returncode
        else:
            print(f"[StarVM] Star compiler not available for {filepath}")
            return 1
