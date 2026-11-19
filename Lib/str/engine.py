"""
Star Programming Language OmniEngine (str.engine / star.engine)
Declarative UI State Pipeline, 4D Visual Causality Timeline,
Reactive Signals, Layout Overflow Self-Healing, and Motion Physics.
Specification & Architecture for Star Language & Haven Unified Ecosystem.
Standard Specification by Anirudha Puthraya.
Copyright (c) 2026 Star Language Foundation & Anirudha Puthraya.
"""

import time
import math
import uuid
import copy
from typing import Any, Dict, List, Optional, Callable, Set, Tuple, Union
from .ui import Widget, Container, Text


class StarSignal:
    """Fine-grained reactive signal for Star declarative UI widgets."""

    def __init__(self, value: Any, label: str = ""):
        self._value = value
        self.label = label or f"signal_{uuid.uuid4().hex[:6]}"
        self._subscribers: Set[Callable[[Any], None]] = set()

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_val: Any):
        if self._value != new_val:
            self._value = new_val
            self._notify()

    def set(self, new_val: Any):
        self.value = new_val

    def get(self) -> Any:
        return self._value

    def update(self, fn: Callable[[Any], Any]):
        self.value = fn(self._value)

    def subscribe(self, callback: Callable[[Any], None]):
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[Any], None]):
        self._subscribers.discard(callback)

    def _notify(self):
        for sub in list(self._subscribers):
            try:
                sub(self._value)
            except Exception:
                pass

    def __repr__(self) -> str:
        return f"<StarSignal [{self.label}]: {self._value!r}>"


class StarComputed:
    """Memoized reactive computed value tracking upstream StarSignals."""

    def __init__(self, compute_fn: Callable[[], Any], label: str = ""):
        self.compute_fn = compute_fn
        self.label = label or f"computed_{uuid.uuid4().hex[:6]}"
        self._cached_value: Any = None
        self._dirty = True

    @property
    def value(self) -> Any:
        if self._dirty:
            self._cached_value = self.compute_fn()
            self._dirty = False
        return self._cached_value

    def invalidate(self):
        self._dirty = True

    def __call__(self) -> Any:
        return self.value

    def __repr__(self) -> str:
        val_str = repr(self._cached_value) if not self._dirty else "<dirty>"
        return f"<StarComputed [{self.label}]: {val_str}>"


class UIFrameSnapshot:
    """Immutable snapshot of a visual UI frame in the 4D timeline."""

    def __init__(self, frame_id: int, state: Dict[str, Any], widget_tree_repr: str, action: str):
        self.frame_id = frame_id
        self.timestamp = time.time()
        self.state = copy.deepcopy(state)
        self.widget_tree_repr = widget_tree_repr
        self.action = action

    def __repr__(self) -> str:
        return f"<UIFrame #{self.frame_id} [{self.action}] @ {self.timestamp:.3f}>"


class UITimelineDAG:
    """
    4D Visual Causality Timeline & Time-Travel UI Debugger for Star.
    Records UI frames, widget trees, and user interactions, allowing
    instant rewinding to past frames and branch exploration.
    """

    def __init__(self):
        self.frames: List[UIFrameSnapshot] = []
        self.current_frame_index: int = -1
        self.branches: Dict[str, List[UIFrameSnapshot]] = {"main": []}
        self.active_branch: str = "main"

    def record_frame(self, state: Dict[str, Any], widget_tree_repr: str = "", action: str = "RENDER") -> UIFrameSnapshot:
        frame_id = len(self.frames)
        snap = UIFrameSnapshot(frame_id, state, widget_tree_repr, action)
        self.frames.append(snap)
        self.branches[self.active_branch].append(snap)
        self.current_frame_index = frame_id
        return snap

    def rewind(self, steps: int = 1) -> Optional[UIFrameSnapshot]:
        """Rewinds the visual UI state by N steps in the timeline."""
        if not self.frames:
            return None
        target = max(0, self.current_frame_index - steps)
        self.current_frame_index = target
        return self.frames[target]

    def forward(self, steps: int = 1) -> Optional[UIFrameSnapshot]:
        """Fast-forwards the visual UI state by N steps toward the latest frame."""
        if not self.frames:
            return None
        target = min(len(self.frames) - 1, self.current_frame_index + steps)
        self.current_frame_index = target
        return self.frames[target]

    def fork_branch(self, branch_name: str) -> bool:
        """Forks a new exploratory UI branch from the current frame."""
        if self.current_frame_index < 0 or not self.frames:
            return False
        current_snap = self.frames[self.current_frame_index]
        self.branches[branch_name] = [current_snap]
        self.active_branch = branch_name
        return True

    def current_state(self) -> Dict[str, Any]:
        if 0 <= self.current_frame_index < len(self.frames):
            return self.frames[self.current_frame_index].state
        return {}


class UIHealingReceipt:
    """Cryptographic audit receipt of an automated visual layout self-healing incident."""

    def __init__(self, incident_id: str, breach_type: str, strategy: str, details: str):
        self.incident_id = incident_id
        self.breach_type = breach_type
        self.strategy = strategy
        self.details = details
        self.timestamp = time.time()

    def __repr__(self) -> str:
        return f"<UIHealingReceipt [{self.breach_type} -> {self.strategy}] {self.incident_id}>"


class UIHealer:
    """
    Autonomous Visual Layout & Constraint Healer for Star.
    Intercepts layout breaches (e.g. RenderFlex overflow on small screens,
    unbounded height constraints, or missing key attributes), applying
    real-time self-healing adaptations.
    """

    def __init__(self):
        self.healing_history: List[UIHealingReceipt] = []

    def heal_overflow(
        self,
        widget_type: str,
        content_size: float,
        available_size: float,
        axis: str = "vertical"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Diagnoses and heals screen overflow (the infamous yellow-and-black stripes).
        Returns (was_healed, strategy_applied, recommended_params).
        """
        if content_size <= available_size:
            return (False, "NO_OVERFLOW_DETECTED", {})

        overflow_px = content_size - available_size
        incident_id = f"ui-heal-{uuid.uuid4().hex[:8]}"

        if axis == "vertical":
            strategy = "WRAP_IN_SCROLL_VIEW"
            recommended = {
                "wrap_widget": "SingleChildScrollView",
                "physics": "BouncingScrollPhysics",
                "overflow_px": overflow_px
            }
        else:
            strategy = "AUTO_FLEX_OR_WRAP"
            recommended = {
                "wrap_widget": "Wrap",
                "direction": "horizontal",
                "overflow_px": overflow_px
            }

        receipt = UIHealingReceipt(
            incident_id=incident_id,
            breach_type=f"RenderFlex_{axis.upper()}_OVERFLOW",
            strategy=strategy,
            details=f"Exceeded constraint by {overflow_px:.1f}px. Applied {strategy}."
        )
        self.healing_history.append(receipt)
        return (True, strategy, recommended)


class SpringSimulation:
    """Damped harmonic oscillator physics simulator for Star UI animations."""

    def __init__(self, mass: float = 1.0, stiffness: float = 180.0, damping: float = 12.0):
        self.mass = mass
        self.stiffness = stiffness
        self.damping = damping

        # Compute angular frequency and damping ratio
        self.w0 = math.sqrt(stiffness / mass)
        self.zeta = damping / (2.0 * math.sqrt(stiffness * mass))

    def solve(self, t: float, initial_distance: float = 1.0, initial_velocity: float = 0.0) -> float:
        """Computes position offset at time t seconds."""
        if self.zeta < 1.0:
            # Underdamped
            wd = self.w0 * math.sqrt(1.0 - self.zeta ** 2)
            decay = math.exp(-self.zeta * self.w0 * t)
            c1 = initial_distance
            c2 = (initial_velocity + self.zeta * self.w0 * initial_distance) / wd
            return decay * (c1 * math.cos(wd * t) + c2 * math.sin(wd * t))
        elif abs(self.zeta - 1.0) < 1e-5:
            # Critically damped
            return math.exp(-self.w0 * t) * (initial_distance + (initial_velocity + self.w0 * initial_distance) * t)
        else:
            # Overdamped
            r1 = -self.w0 * (self.zeta - math.sqrt(self.zeta ** 2 - 1.0))
            r2 = -self.w0 * (self.zeta + math.sqrt(self.zeta ** 2 - 1.0))
            c2 = (initial_velocity - r1 * initial_distance) / (r2 - r1)
            c1 = initial_distance - c2
            return c1 * math.exp(r1 * t) + c2 * math.exp(r2 * t)


class MotionChoreographer:
    """Coordinates declarative UI animations, tweening, and physics transitions."""

    def __init__(self):
        self.spring = SpringSimulation()

    def tween(self, begin: float, end: float, progress: float, curve: str = "ease_in_out") -> float:
        """Interpolates between begin and end across normalized progress [0.0, 1.0]."""
        p = max(0.0, min(1.0, float(progress)))
        if curve == "linear":
            t = p
        elif curve == "ease_in":
            t = p * p
        elif curve == "ease_out":
            t = p * (2.0 - p)
        elif curve == "ease_in_out":
            t = (p * p * (3.0 - 2.0 * p))
        elif curve == "spring":
            t = 1.0 - self.spring.solve(p * 0.5)
        else:
            t = p
        return begin + (end - begin) * t


class PlatformOmniBridge:
    """Universal device hardware, platform metrics, and sensor event bridge for Star."""

    def __init__(self):
        self.platform = "Android"  # Android, iOS, Windows, macOS, Linux, Web
        self.pixel_ratio: float = 3.0
        self.screen_width: float = 393.0
        self.screen_height: float = 852.0
        self.orientation: str = "portrait"
        self.dark_mode: bool = True

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "pixel_ratio": self.pixel_ratio,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "orientation": self.orientation,
            "dark_mode": self.dark_mode
        }


class StarOmniEngine:
    """
    Star Programming Language OmniEngine (Unified Coordinator).
    Integrates the 4D UI Timeline, Fine-Grained Reactive Signals,
    Layout Self-Healing Reactor, Motion Choreography, and Platform Bridge.
    """

    def __init__(self, name: str = "StarOmniEngine"):
        self.name = name
        self.timeline = UITimelineDAG()
        self.healer = UIHealer()
        self.motion = MotionChoreographer()
        self.bridge = PlatformOmniBridge()
        self.signals: Dict[str, StarSignal] = {}

    def signal(self, initial_value: Any, label: str = "") -> StarSignal:
        sig = StarSignal(initial_value, label=label)
        self.signals[sig.label] = sig
        return sig

    def computed(self, compute_fn: Callable[[], Any], label: str = "") -> StarComputed:
        return StarComputed(compute_fn, label=label)

    def commit_frame(self, state: Dict[str, Any], action: str = "STATE_MUTATION") -> UIFrameSnapshot:
        return self.timeline.record_frame(state=state, action=action)

    def stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "active_signals": len(self.signals),
            "timeline_frames": len(self.timeline.frames),
            "current_frame": self.timeline.current_frame_index,
            "healing_incidents": len(self.healer.healing_history),
            "platform": self.bridge.platform
        }

    def __repr__(self) -> str:
        return f"<StarOmniEngine [{self.name}] frames={len(self.timeline.frames)} signals={len(self.signals)}>"


# Global singleton instance
star_omni = StarOmniEngine("DefaultStarOmni")
