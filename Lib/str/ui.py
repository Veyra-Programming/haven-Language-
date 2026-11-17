"""
Star Language Flutter Universal Declarative UI Subsystem
Zero-JS Flutter / Material Declarative Widget Hierarchy
Specification & Architecture for Star Language & Haven Unified Ecosystem.
"""

from typing import Any, Dict, List, Optional, Union, Callable


class Widget:
    """Base class for all Star declarative UI components."""
    def __init__(self, **kwargs):
        self._props = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.__class__.__name__}
        for k, v in self._props.items():
            if isinstance(v, Widget):
                d[k] = v.to_dict()
            elif isinstance(v, list):
                d[k] = [x.to_dict() if isinstance(x, Widget) else x for x in v]
            else:
                d[k] = str(v)
        return d

    def render_tui(self, indent: int = 0) -> str:
        pad = "  " * indent
        name = self.__class__.__name__
        lines = [f"{pad}<{name}"]
        for k, v in self._props.items():
            if k in ("children", "child", "body"):
                continue
            lines.append(f"{pad}  {k}={v!r}")
        lines[-1] = lines[-1] + ">" if len(lines) > 1 else f"{pad}<{name}>"
        
        # Render body or children
        if "body" in self._props and isinstance(self._props["body"], Widget):
            lines.append(self._props["body"].render_tui(indent + 1))
        if "child" in self._props and isinstance(self._props["child"], Widget):
            lines.append(self._props["child"].render_tui(indent + 1))
        if "children" in self._props and isinstance(self._props["children"], list):
            for ch in self._props["children"]:
                if isinstance(ch, Widget):
                    lines.append(ch.render_tui(indent + 1))
                else:
                    lines.append(f"{pad}  {ch!r}")
        lines.append(f"{pad}</{name}>")
        return "\n".join(lines)

    def __repr__(self) -> str:
        props_str = ", ".join(f"{k}={v!r}" for k, v in self._props.items())
        return f"{self.__class__.__name__}({props_str})"


# ==========================================
# 1. Structural Widgets
# ==========================================

class Scaffold(Widget):
    def __init__(self, appBar=None, body=None, backgroundColor=None,
                 floatingActionButton=None, bottomNavigationBar=None,
                 elevation=None, drawer=None, **kwargs):
        super().__init__(appBar=appBar, body=body, backgroundColor=backgroundColor,
                         floatingActionButton=floatingActionButton,
                         bottomNavigationBar=bottomNavigationBar,
                         elevation=elevation, drawer=drawer, **kwargs)


class AppBar(Widget):
    def __init__(self, title=None, backgroundColor=None, elevation=None,
                 actions=None, leading=None, **kwargs):
        super().__init__(title=title, backgroundColor=backgroundColor,
                         elevation=elevation, actions=actions, leading=leading, **kwargs)


class BottomNavigationBar(Widget):
    def __init__(self, items=None, currentIndex=0, onTap=None, backgroundColor=None, **kwargs):
        super().__init__(items=items or [], currentIndex=currentIndex,
                         onTap=onTap, backgroundColor=backgroundColor, **kwargs)


class FloatingActionButton(Widget):
    def __init__(self, child=None, onPressed=None, backgroundColor=None, tooltip=None, **kwargs):
        super().__init__(child=child, onPressed=onPressed,
                         backgroundColor=backgroundColor, tooltip=tooltip, **kwargs)


class SafeArea(Widget):
    def __init__(self, child=None, top=True, bottom=True, left=True, right=True, **kwargs):
        super().__init__(child=child, top=top, bottom=bottom, left=left, right=right, **kwargs)


# ==========================================
# 2. Layout Widgets
# ==========================================

class Column(Widget):
    def __init__(self, children=None, mainAxisAlignment="start",
                 crossAxisAlignment="start", **kwargs):
        super().__init__(children=children or [],
                         mainAxisAlignment=mainAxisAlignment,
                         crossAxisAlignment=crossAxisAlignment, **kwargs)


class Row(Widget):
    def __init__(self, children=None, mainAxisAlignment="start",
                 crossAxisAlignment="start", **kwargs):
        super().__init__(children=children or [],
                         mainAxisAlignment=mainAxisAlignment,
                         crossAxisAlignment=crossAxisAlignment, **kwargs)


class Stack(Widget):
    def __init__(self, children=None, alignment="topStart", **kwargs):
        super().__init__(children=children or [], alignment=alignment, **kwargs)


class Positioned(Widget):
    def __init__(self, child=None, top=None, bottom=None, left=None, right=None,
                 width=None, height=None, **kwargs):
        super().__init__(child=child, top=top, bottom=bottom, left=left, right=right,
                         width=width, height=height, **kwargs)


class Container(Widget):
    def __init__(self, child=None, width=None, height=None, margin=None,
                 padding=None, decoration=None, color=None, **kwargs):
        super().__init__(child=child, width=width, height=height, margin=margin,
                         padding=padding, decoration=decoration, color=color, **kwargs)


class Padding(Widget):
    def __init__(self, padding=None, child=None, **kwargs):
        super().__init__(padding=padding, child=child, **kwargs)


class Center(Widget):
    def __init__(self, child=None, **kwargs):
        super().__init__(child=child, **kwargs)


class Expanded(Widget):
    def __init__(self, child=None, flex=1, **kwargs):
        super().__init__(child=child, flex=flex, **kwargs)


class SizedBox(Widget):
    def __init__(self, width=None, height=None, child=None, **kwargs):
        super().__init__(width=width, height=height, child=child, **kwargs)


class Wrap(Widget):
    def __init__(self, children=None, spacing=0.0, runSpacing=0.0, **kwargs):
        super().__init__(children=children or [], spacing=spacing, runSpacing=runSpacing, **kwargs)


class Spacer(Widget):
    def __init__(self, flex=1, **kwargs):
        super().__init__(flex=flex, **kwargs)


# ==========================================
# 3. Interactive Widgets
# ==========================================

class GestureDetector(Widget):
    def __init__(self, child=None, onTap=None, onDoubleTap=None, onLongPress=None, **kwargs):
        super().__init__(child=child, onTap=onTap, onDoubleTap=onDoubleTap,
                         onLongPress=onLongPress, **kwargs)


class ElevatedButton(Widget):
    def __init__(self, child=None, onPressed=None, style=None, **kwargs):
        super().__init__(child=child, onPressed=onPressed, style=style, **kwargs)


class InkWell(Widget):
    def __init__(self, child=None, onTap=None, **kwargs):
        super().__init__(child=child, onTap=onTap, **kwargs)


class CupertinoButton(Widget):
    def __init__(self, child=None, onPressed=None, color=None, **kwargs):
        super().__init__(child=child, onPressed=onPressed, color=color, **kwargs)


class IconButton(Widget):
    def __init__(self, icon=None, onPressed=None, tooltip=None, **kwargs):
        super().__init__(icon=icon, onPressed=onPressed, tooltip=tooltip, **kwargs)


# ==========================================
# 4. Content Widgets
# ==========================================

class Text(Widget):
    def __init__(self, data="", style=None, textAlign=None, maxLines=None, overflow=None, **kwargs):
        super().__init__(data=data, style=style, textAlign=textAlign,
                         maxLines=maxLines, overflow=overflow, **kwargs)


class Image(Widget):
    def __init__(self, src="", fit=None, width=None, height=None, **kwargs):
        super().__init__(src=src, fit=fit, width=width, height=height, **kwargs)

    @classmethod
    def network(cls, url: str, fit=None, width=None, height=None, **kwargs):
        return cls(src=url, fit=fit, width=width, height=height, is_network=True, **kwargs)

    @classmethod
    def asset(cls, path: str, fit=None, width=None, height=None, **kwargs):
        return cls(src=path, fit=fit, width=width, height=height, is_asset=True, **kwargs)


class Icon(Widget):
    def __init__(self, icon_data=None, size=None, color=None, **kwargs):
        super().__init__(icon_data=icon_data, size=size, color=color, **kwargs)


class Card(Widget):
    def __init__(self, child=None, elevation=None, color=None, shape=None, **kwargs):
        super().__init__(child=child, elevation=elevation, color=color, shape=shape, **kwargs)


class ListView(Widget):
    def __init__(self, children=None, scrollDirection="vertical", **kwargs):
        super().__init__(children=children or [], scrollDirection=scrollDirection, **kwargs)

    @classmethod
    def builder(cls, itemCount: int = 0, itemBuilder=None, **kwargs):
        children = []
        if callable(itemBuilder):
            children = [itemBuilder(i) for i in range(itemCount)]
        return cls(children=children, itemCount=itemCount, **kwargs)


class GridView(Widget):
    def __init__(self, children=None, crossAxisCount=2, spacing=8.0, **kwargs):
        super().__init__(children=children or [], crossAxisCount=crossAxisCount,
                         spacing=spacing, **kwargs)


# ==========================================
# 5. Conditional & State Widgets
# ==========================================

class When(Widget):
    def __init__(self, condition: bool, trueWidget, falseWidget=None, **kwargs):
        chosen = trueWidget if condition else falseWidget
        super().__init__(condition=condition, active=chosen, **kwargs)

    def render_tui(self, indent: int = 0) -> str:
        if self._props.get("active") and isinstance(self._props["active"], Widget):
            return self._props["active"].render_tui(indent)
        return ""


class SwitchCase(Widget):
    def __init__(self, value: Any, cases: Optional[Dict[Any, Any]] = None,
                 defaultWidget=None, **kwargs):
        cases = cases or {}
        active = cases.get(value, defaultWidget)
        super().__init__(value=value, active=active, **kwargs)


class Visibility(Widget):
    def __init__(self, child=None, visible=True, **kwargs):
        super().__init__(child=child, visible=visible, **kwargs)


class Opacity(Widget):
    def __init__(self, opacity=1.0, child=None, **kwargs):
        super().__init__(opacity=opacity, child=child, **kwargs)


# ==========================================
# 6. Styling, Layout & Theming Primitives
# ==========================================

class Color:
    def __init__(self, value: Union[int, str]):
        if isinstance(value, str):
            if value.startswith("#"):
                value = int(value[1:], 16)
            elif value.startswith("0x") or value.startswith("0X"):
                value = int(value, 16)
            else:
                value = int(value, 16)
        self.value = value

    def __repr__(self) -> str:
        return f"Color(0x{self.value:08X})"

    def __str__(self) -> str:
        return f"0x{self.value:08X}"


class Colors:
    transparent = Color(0x00000000)
    black = Color(0xFF000000)
    black87 = Color(0xDD000000)
    white = Color(0xFFFFFFFF)
    red = Color(0xFFE53935)
    pink = Color(0xFFD81B60)
    purple = Color(0xFF8E24AA)
    indigo = Color(0xFF3F51B5)
    blue = Color(0xFF1E88E5)
    cyan = Color(0xFF00ACC1)
    teal = Color(0xFF00897B)
    green = Color(0xFF43A047)
    yellow = Color(0xFFFDD835)
    amber = Color(0xFFFFB300)
    orange = Color(0xFFFB8C00)
    grey = Color(0xFF757575)


class Icons:
    home = "icon_home"
    search = "icon_search"
    settings = "icon_settings"
    favorite = "icon_favorite"
    share = "icon_share"
    arrow_back = "icon_arrow_back"
    wallpaper = "icon_wallpaper"
    star = "icon_star"
    download = "icon_download"
    check = "icon_check"
    close = "icon_close"
    refresh = "icon_refresh"


class TextStyle:
    def __init__(self, fontSize=14.0, fontWeight="normal", color=None,
                 fontFamily=None, letterSpacing=None):
        self.fontSize = fontSize
        self.fontWeight = fontWeight
        self.color = color
        self.fontFamily = fontFamily
        self.letterSpacing = letterSpacing

    def __repr__(self) -> str:
        return f"TextStyle(fontSize={self.fontSize}, fontWeight={self.fontWeight!r}, color={self.color})"


class FontWeight:
    w100 = "w100"
    w200 = "w200"
    w300 = "w300"
    w400 = "w400"
    w500 = "w500"
    w600 = "w600"
    w700 = "w700"
    w800 = "w800"
    w900 = "w900"
    normal = "w400"
    bold = "w700"


class EdgeInsets:
    def __init__(self, top=0.0, bottom=0.0, left=0.0, right=0.0):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    @classmethod
    def all(cls, value: float):
        return cls(value, value, value, value)

    @classmethod
    def symmetric(cls, horizontal: float = 0.0, vertical: float = 0.0):
        return cls(top=vertical, bottom=vertical, left=horizontal, right=horizontal)

    @classmethod
    def only(cls, top: float = 0.0, bottom: float = 0.0, left: float = 0.0, right: float = 0.0):
        return cls(top=top, bottom=bottom, left=left, right=right)

    def __repr__(self) -> str:
        return f"EdgeInsets(top={self.top}, bottom={self.bottom}, left={self.left}, right={self.right})"


class BorderRadius:
    def __init__(self, radius: float = 0.0):
        self.radius = radius

    @classmethod
    def circular(cls, radius: float):
        return cls(radius)

    @classmethod
    def all(cls, radius: float):
        return cls(radius)

    def __repr__(self) -> str:
        return f"BorderRadius.circular({self.radius})"


class BoxShadow:
    def __init__(self, color=None, blurRadius: float = 0.0, spreadRadius: float = 0.0, offset=(0, 0)):
        self.color = color
        self.blurRadius = blurRadius
        self.spreadRadius = spreadRadius
        self.offset = offset

    def __repr__(self) -> str:
        return f"BoxShadow(color={self.color}, blurRadius={self.blurRadius})"


class LinearGradient:
    def __init__(self, colors=None, begin="topLeft", end="bottomRight"):
        self.colors = colors or []
        self.begin = begin
        self.end = end

    def __repr__(self) -> str:
        return f"LinearGradient(colors={self.colors}, begin={self.begin!r}, end={self.end!r})"


class BoxDecoration:
    def __init__(self, color=None, borderRadius=None, boxShadow=None, gradient=None, border=None):
        self.color = color
        self.borderRadius = borderRadius
        self.boxShadow = boxShadow or []
        self.gradient = gradient
        self.border = border

    def __repr__(self) -> str:
        return f"BoxDecoration(color={self.color}, borderRadius={self.borderRadius})"


class MainAxisAlignment:
    start = "start"
    center = "center"
    end = "end"
    spaceBetween = "spaceBetween"
    spaceAround = "spaceAround"
    spaceEvenly = "spaceEvenly"


class CrossAxisAlignment:
    start = "start"
    center = "center"
    end = "end"
    stretch = "stretch"


class BoxFit:
    cover = "cover"
    contain = "contain"
    fill = "fill"
    fitWidth = "fitWidth"
    fitHeight = "fitHeight"
    none = "none"
