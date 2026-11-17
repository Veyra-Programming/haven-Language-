"""
Flutter Declarative UI Subsystem for Star & Haven
"""
import str as _str

for attr in dir(_str):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_str, attr)
