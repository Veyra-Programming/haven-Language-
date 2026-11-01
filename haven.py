"""
Haven Language CLI Entry Point
Open Digital Continuity Standard (ODCS) by Anirudha Puthraya.
"""
# pyright: reportMissingImports=false
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
lib_dir = str(os.path.join(here, "Lib"))
if os.path.isdir(lib_dir):
    if lib_dir in sys.path:
        sys.path.remove(lib_dir)
    sys.path.insert(0, lib_dir)

try:
    from haven.cli.main import main  # type: ignore[import-not-found]
except ImportError:
    import importlib.util
    main_py = os.path.join(lib_dir, "haven", "cli", "main.py")
    spec = importlib.util.spec_from_file_location("haven.cli.main", main_py)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["haven.cli.main"] = mod
        spec.loader.exec_module(mod)
        main = getattr(mod, "main")
    else:
        raise

if __name__ == '__main__':
    sys.exit(main())
