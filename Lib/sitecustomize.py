"""
Haven Programming Language (ODCS Native Edition) Site Customization
Standard Architecture by Anirudha Puthraya
"""
import builtins

try:
    import _sitebuiltins
    _sitebuiltins._Helper.__repr__ = lambda self: "Type help() for Haven interactive help, or help(object) for help about object."
    builtins.help = _sitebuiltins._Helper()
except Exception:
    pass

