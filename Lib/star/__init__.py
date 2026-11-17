"""
Star Language Universal Standard Library Gateway (star alias for str)
"""
import sys
import str as _str

# Forward all attributes
for attr in dir(_str):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_str, attr)

sys.modules["star"] = _str
