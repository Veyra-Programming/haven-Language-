"""
Haven Programming Language (ODCS Native Edition v2.1.1 GA) Site Customization
Standard Architecture by Anirudha Puthraya
"""
import builtins
import sys
from importlib.abc import MetaPathFinder

# Enforce Haven & ODCS runtime identity
sys.version = "Haven 2.1.1 GA (ODCS Native Production Core) [Windows/MSVC]"

try:
    import _sitebuiltins
    _sitebuiltins._Helper.__repr__ = lambda self: "Type help() for Haven interactive help, or help(object) for ODCS and language object help."
    builtins.help = _sitebuiltins._Helper()
    builtins.nothing = None
except Exception:
    builtins.nothing = None

class _CaseAndAliasFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "Hvn":
            import hvn
            sys.modules["Hvn"] = hvn
            return getattr(hvn, "__spec__", None)
        elif fullname.startswith("Hvn."):
            real_name = "hvn." + fullname[4:]
            __import__(real_name)
            mod = sys.modules.get(real_name)
            if mod is not None:
                sys.modules[fullname] = mod
                return getattr(mod, "__spec__", None)
        elif fullname in ("Flutter", "Material"):
            import str as star_mod
            sys.modules[fullname] = star_mod
            return getattr(star_mod, "__spec__", None)
        return None

sys.meta_path.insert(0, _CaseAndAliasFinder())


