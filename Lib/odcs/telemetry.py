"""
Open Digital Continuity Standard (ODCS) - Layer 3: Runtime & Environmental Adaptation
Standard Specification & Architecture by Anirudha Puthraya.
Implements:
  - ContinuityMode: Operational connectivity states
  - EnvironmentalTelemetry: Real-time RTT probing, packet loss, battery, and mode determination
  - adaptive_policy: Function decorator for seamless operational degradation
"""

from enum import Enum
from typing import Callable, Any, Optional, Dict
import time
import socket
import functools


class ContinuityMode(Enum):
    """ODCS Layer 3 Operational Runtime Modes."""
    FULL_CONNECTIVITY = "full"             # High bandwidth (< 100ms RTT, 0% loss)
    DEGRADED_BANDWIDTH = "degraded"        # Constrained network (100-500ms RTT, low throughput)
    HIGH_LATENCY_SAT = "satellite"         # Satellite link (> 500ms RTT, intermittent jitter)
    AIRGAP_OFFLINE = "airgap"              # Complete disconnection, zero socket access


class EnvironmentalTelemetry:
    """
    Environmental Telemetry Engine (ODCS Layer 3.1).
    Probes runtime environment to establish dynamic operational mode.
    """
    _override_mode: Optional[ContinuityMode] = None

    def __init__(self, probe_target: str = "1.1.1.1", probe_port: int = 53):
        self.probe_target = probe_target
        self.probe_port = probe_port
        self.last_probe_time: float = 0
        self.cached_rtt_ms: float = 0.0
        self.cached_mode: ContinuityMode = ContinuityMode.AIRGAP_OFFLINE

    @classmethod
    def set_override(cls, mode: Optional[ContinuityMode]) -> None:
        """Manually force an operational mode (useful for testing and airgap drill simulations)."""
        cls._override_mode = mode

    def probe(self, timeout_sec: float = 0.6) -> ContinuityMode:
        """Probe socket connectivity and compute operational mode."""
        if self._override_mode is not None:
            self.cached_mode = self._override_mode
            return self.cached_mode

        t0 = time.perf_counter()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_sec)
            sock.connect((self.probe_target, self.probe_port))
            sock.close()
            rtt_ms = (time.perf_counter() - t0) * 1000.0
            self.cached_rtt_ms = rtt_ms

            if rtt_ms < 120:
                self.cached_mode = ContinuityMode.FULL_CONNECTIVITY
            elif rtt_ms < 500:
                self.cached_mode = ContinuityMode.DEGRADED_BANDWIDTH
            else:
                self.cached_mode = ContinuityMode.HIGH_LATENCY_SAT
        except Exception:
            self.cached_rtt_ms = 9999.0
            self.cached_mode = ContinuityMode.AIRGAP_OFFLINE

        self.last_probe_time = time.time()
        return self.cached_mode

    def status_summary(self) -> Dict[str, Any]:
        """Returns clean status dictionary for telemetry displays."""
        mode = self.probe()
        return {
            "mode": mode.value,
            "mode_label": mode.name,
            "rtt_ms": round(self.cached_rtt_ms, 2) if self.cached_rtt_ms < 9000 else None,
            "is_online": mode != ContinuityMode.AIRGAP_OFFLINE,
            "is_airgapped": mode == ContinuityMode.AIRGAP_OFFLINE,
            "timestamp": time.time(),
        }


def adaptive_policy(
    on_airgap: Optional[Callable] = None,
    on_degraded: Optional[Callable] = None
):
    """
    ODCS Layer 3 Adaptive Execution Decorator.
    Executes primary function when FULL_CONNECTIVITY is available.
    Automatically degrades to on_degraded or on_airgap when network is disrupted.
    """
    telemetry = EnvironmentalTelemetry()

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            mode = telemetry.probe()
            if mode == ContinuityMode.AIRGAP_OFFLINE and on_airgap is not None:
                return on_airgap(*args, **kwargs)
            elif mode in (ContinuityMode.DEGRADED_BANDWIDTH, ContinuityMode.HIGH_LATENCY_SAT) and on_degraded is not None:
                return on_degraded(*args, **kwargs)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

