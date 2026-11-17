"""
Hvn / Haven Standard System Library v2.1.1 GA
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Specification & Architecture by Anirudha Puthraya.
Unified 'hvn' and 'Hvn' Initial Package Gateway.
"""

import sys
import types
import haven

# Copy all attributes from haven
for attr in dir(haven):
    if not attr.startswith("__"):
        globals()[attr] = getattr(haven, attr)

# Import all 199+ standard methods
try:
    from haven.methods import *
except ImportError:
    pass

# Convenience aliases
sha256 = getattr(haven, "sha256_hex", getattr(haven, "sha256_digest", None))

# Expose key first-class submodules
try:
    import haven.units as units
except ImportError:
    units = None

try:
    import haven.intent as intent
except ImportError:
    intent = None

try:
    import haven.methods as methods
except ImportError:
    methods = None

try:
    import haven.flow as flow
except ImportError:
    flow = None

try:
    import haven.neural as neural
except ImportError:
    neural = None

try:
    import haven.iot as iot
except ImportError:
    iot = None

try:
    import haven.zk as zk
except ImportError:
    zk = None

try:
    import haven.agents as agents
except ImportError:
    agents = None

try:
    import haven.continuity as continuity
except ImportError:
    continuity = None

try:
    import haven.algorithm as algorithm
except ImportError:
    algorithm = None

# Ensure both 'hvn' and 'Hvn' alias to this package in sys.modules
this_mod = sys.modules[__name__]
sys.modules['Hvn'] = this_mod
sys.modules['hvn'] = this_mod

if units is not None:
    sys.modules['hvn.units'] = units
    sys.modules['Hvn.units'] = units
if intent is not None:
    sys.modules['hvn.intent'] = intent
    sys.modules['Hvn.intent'] = intent
if methods is not None:
    sys.modules['hvn.methods'] = methods
    sys.modules['Hvn.methods'] = methods
if flow is not None:
    sys.modules['hvn.flow'] = flow
    sys.modules['Hvn.flow'] = flow
if neural is not None:
    sys.modules['hvn.neural'] = neural
    sys.modules['Hvn.neural'] = neural
if iot is not None:
    sys.modules['hvn.iot'] = iot
    sys.modules['Hvn.iot'] = iot
if zk is not None:
    sys.modules['hvn.zk'] = zk
    sys.modules['Hvn.zk'] = zk
if agents is not None:
    sys.modules['hvn.agents'] = agents
    sys.modules['Hvn.agents'] = agents
if continuity is not None:
    sys.modules['hvn.continuity'] = continuity
    sys.modules['Hvn.continuity'] = continuity
if algorithm is not None:
    sys.modules['hvn.algorithm'] = algorithm
    sys.modules['Hvn.algorithm'] = algorithm

__all__ = [k for k in globals().keys() if not k.startswith("_")]
