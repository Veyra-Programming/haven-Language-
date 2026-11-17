"""
Star Language Universal Standard Library v1.2.0
Zero-JS Flutter UI, Cross-Platform Engine & Native Mobile Bridges
Specification & Architecture for Star Language & Haven Unified Ecosystem.
Callable 'str' Package Gateway with Built-in String Preservation.
"""

import sys
import os
import builtins
import types

from . import ui
from . import mobile
from . import vm

from .ui import (
    Widget,
    Scaffold,
    AppBar,
    BottomNavigationBar,
    FloatingActionButton,
    SafeArea,
    Column,
    Row,
    Stack,
    Positioned,
    Container,
    Padding,
    Center,
    Expanded,
    SizedBox,
    Wrap,
    Spacer,
    GestureDetector,
    ElevatedButton,
    InkWell,
    CupertinoButton,
    IconButton,
    Text,
    Image,
    Icon,
    Card,
    ListView,
    GridView,
    When,
    SwitchCase,
    Visibility,
    Opacity,
    Color,
    Colors,
    Icons,
    TextStyle,
    FontWeight,
    EdgeInsets,
    BorderRadius,
    BoxShadow,
    LinearGradient,
    BoxDecoration,
    MainAxisAlignment,
    CrossAxisAlignment,
    BoxFit,
)

from .mobile import (
    AndroidWallpaperService,
    AndroidHapticService,
    Mobile,
    GoogleBillingClient,
)

from .vm import (
    StarApp,
    StarVM,
)

# =====================================================================
# Callable Module / Class Implementation:
# Allows `use str` or `import str` while retaining `str(val)` callability
# and `isinstance(val, str)` compatibility for all standard Python/Haven code.
# =====================================================================

class _StarMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, builtins.str)

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, builtins.str)

    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            return ""
        return builtins.str(*args, **kwargs)


class StarPackage(builtins.str, metaclass=_StarMeta):
    """
    Unified Star Language Runtime & Callable String Module.
    Combines Star Language declarative UI, mobile bridges, and stack machine
    with standard string conversion without namespace pollution.
    """
    pass


# Bind submodules and attributes to StarPackage
pkg_dir = os.path.dirname(os.path.abspath(__file__))
StarPackage.__name__ = "str"
StarPackage.__package__ = "str"
StarPackage.__file__ = os.path.join(pkg_dir, "__init__.py")
StarPackage.__path__ = [pkg_dir]
StarPackage.__doc__ = __doc__

# Submodules
StarPackage.ui = ui
StarPackage.mobile = mobile
StarPackage.vm = vm

# Structural Widgets
StarPackage.Widget = Widget
StarPackage.Scaffold = Scaffold
StarPackage.AppBar = AppBar
StarPackage.BottomNavigationBar = BottomNavigationBar
StarPackage.FloatingActionButton = FloatingActionButton
StarPackage.SafeArea = SafeArea

# Layout Widgets
StarPackage.Column = Column
StarPackage.Row = Row
StarPackage.Stack = Stack
StarPackage.Positioned = Positioned
StarPackage.Container = Container
StarPackage.Padding = Padding
StarPackage.Center = Center
StarPackage.Expanded = Expanded
StarPackage.SizedBox = SizedBox
StarPackage.Wrap = Wrap
StarPackage.Spacer = Spacer

# Interactive Widgets
StarPackage.GestureDetector = GestureDetector
StarPackage.ElevatedButton = ElevatedButton
StarPackage.InkWell = InkWell
StarPackage.CupertinoButton = CupertinoButton
StarPackage.IconButton = IconButton

# Content Widgets
StarPackage.Text = Text
StarPackage.Image = Image
StarPackage.Icon = Icon
StarPackage.Card = Card
StarPackage.ListView = ListView
StarPackage.GridView = GridView

# Conditional & State
StarPackage.When = When
StarPackage.SwitchCase = SwitchCase
StarPackage.Visibility = Visibility
StarPackage.Opacity = Opacity

# Styling & Layout
StarPackage.Color = Color
StarPackage.Colors = Colors
StarPackage.Icons = Icons
StarPackage.TextStyle = TextStyle
StarPackage.FontWeight = FontWeight
StarPackage.EdgeInsets = EdgeInsets
StarPackage.BorderRadius = BorderRadius
StarPackage.BoxShadow = BoxShadow
StarPackage.LinearGradient = LinearGradient
StarPackage.BoxDecoration = BoxDecoration
StarPackage.MainAxisAlignment = MainAxisAlignment
StarPackage.CrossAxisAlignment = CrossAxisAlignment
StarPackage.BoxFit = BoxFit

# Mobile & VM
StarPackage.AndroidWallpaperService = AndroidWallpaperService
StarPackage.AndroidHapticService = AndroidHapticService
StarPackage.Mobile = Mobile
StarPackage.GoogleBillingClient = GoogleBillingClient
StarPackage.StarApp = StarApp
StarPackage.StarVM = StarVM

# Register in sys.modules
sys.modules["str"] = StarPackage
sys.modules["star"] = StarPackage
sys.modules["str.ui"] = ui
sys.modules["str.mobile"] = mobile
sys.modules["str.vm"] = vm
sys.modules["star.ui"] = ui
sys.modules["star.mobile"] = mobile
sys.modules["star.vm"] = vm
