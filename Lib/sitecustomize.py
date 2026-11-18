"""
Ani++ / Haven Programming Language Site Customization
Standard Architecture & Specification by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""
import builtins
import sys
import os
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

# Enforce Ani++ / Haven runtime identity
sys.version = "Ani++ 3.0.0 / Haven 2.1.1 GA (ODCS Native Core) [Windows/MSVC]"

try:
    import _sitebuiltins
    _sitebuiltins._Helper.__repr__ = lambda self: "Type help() for Ani++ / Haven interactive help, or help(object) for ODCS and language object help."
    builtins.help = _sitebuiltins._Helper()
    builtins.nothing = None
except Exception:
    builtins.nothing = None


class HavenSourceLoader(Loader):
    """Loader that transpiles .hvn, .haven, and .ani source files on-the-fly."""
    def __init__(self, fullname: str, path: str):
        self.fullname = fullname
        self.path = path

    def create_module(self, spec):
        return None  # default module creation

    def exec_module(self, module):
        module.__file__ = self.path
        with open(self.path, "r", encoding="utf-8") as f:
            code_text = f.read()

        from haven.transpiler import preprocess_haven
        processed_code = preprocess_haven(code_text)
        compiled = compile(processed_code, self.path, "exec")
        exec(compiled, module.__dict__)


class _AniHavenMetaPathFinder(MetaPathFinder):
    """
    Universal MetaPathFinder resolving:
      1. .ani, .hvn, .haven script module imports (e.g. 'from src.main import ...')
      2. 'hvn', 'ani', 'Hvn', 'str', 'Flutter', 'Material' module aliases
    """
    def find_spec(self, fullname, path, target=None):
        # 1. Aliases
        if fullname in ("hvn", "Hvn"):
            try:
                import haven
                sys.modules[fullname] = haven
                return getattr(haven, "__spec__", None)
            except Exception:
                pass
        elif fullname.startswith(("hvn.", "Hvn.")):
            prefix = "hvn." if fullname.startswith("hvn.") else "Hvn."
            real_name = "haven." + fullname[len(prefix):]
            try:
                __import__(real_name)
                mod = sys.modules.get(real_name)
                if mod is not None:
                    sys.modules[fullname] = mod
                    return getattr(mod, "__spec__", None)
            except Exception:
                pass
        elif fullname in ("Flutter", "Material"):
            try:
                import str as star_mod
                sys.modules[fullname] = star_mod
                return getattr(star_mod, "__spec__", None)
            except Exception:
                pass
        elif fullname == "ani":
            try:
                import ani
                return getattr(ani, "__spec__", None)
            except Exception:
                pass

        # 2. File resolution for .hvn, .haven, .ani in search paths
        search_dirs = list(path) if path else [os.getcwd()] + sys.path
        mod_name = fullname.split(".")[-1]

        for d in search_dirs:
            if not isinstance(d, str) or not os.path.isdir(d):
                continue
            for ext in (".hvn", ".haven", ".ani", ".ani++"):
                candidate = os.path.join(d, mod_name + ext)
                if os.path.isfile(candidate):
                    loader = HavenSourceLoader(fullname, candidate)
                    return ModuleSpec(fullname, loader, origin=candidate)

        return None


# Insert as priority-1 loader
sys.meta_path.insert(0, _AniHavenMetaPathFinder())
