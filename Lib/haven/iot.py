"""
Haven Edge Hardware & IoT Telemetry Standard (HavenIoT)
Standard: Open Digital Continuity Standard (ODCS) Physical Systems Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides dimensional sensor readings, fail-safe actuator controls,
and autonomic airgap survival supervisors for industrial and edge devices.
"""

import time
import uuid
from typing import Any, Dict, Optional, Callable

from .units import UnitQuantity
from .continuity import checkpoint
from .immutability import ContinuityImmutabilityError


class ActuatorSafetyViolation(Exception):
    """Raised when an actuator command violates configured physical safety bounds."""
    pass


class SensorTelemetry:
    """
    A verified, hardware-timestamped sensor telemetry reading bound to
    a dimensional physical unit.
    """
    def __init__(
        self,
        device_id: str,
        sensor_type: str,
        reading: Any,  # May be a UnitQuantity or numerical value
        quality: float = 1.0,
        timestamp_ms: Optional[int] = None
    ):
        self.reading_id = f"tele-{uuid.uuid4().hex[:8]}"
        self.device_id = device_id
        self.sensor_type = sensor_type
        self.reading = reading
        self.quality = max(0.0, min(1.0, float(quality)))
        self.timestamp_ms = timestamp_ms or int(time.time() * 1000)
        self._sealed = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_sealed", False):
            raise ContinuityImmutabilityError("SensorTelemetry is sealed and immutable.")
        super().__setattr__(name, value)

    def is_within_bounds(self, min_val: Any, max_val: Any) -> bool:
        """Evaluates whether reading is within acceptable safe operational bounds."""
        val = self.reading.magnitude if isinstance(self.reading, UnitQuantity) else self.reading
        min_v = min_val.magnitude if isinstance(min_val, UnitQuantity) else min_val
        max_v = max_val.magnitude if isinstance(max_val, UnitQuantity) else max_val
        return min_v <= val <= max_v

    def checkpoint_reading(self, ledger: Optional[Any] = None) -> Any:
        return checkpoint(
            {
                "reading_id": self.reading_id,
                "device_id": self.device_id,
                "sensor_type": self.sensor_type,
                "reading": str(self.reading),
                "quality": self.quality,
                "timestamp_ms": self.timestamp_ms
            },
            alias=f"sensor_{self.sensor_type}",
            ledger=ledger
        )

    def __repr__(self) -> str:
        return f"<SensorTelemetry [{self.device_id}:{self.sensor_type}] = {self.reading} (Q={self.quality:.2f})>"


class ActuatorController:
    """
    Hardware actuator interface with strictly enforced invariant bounds
    and audit trail persistence.
    """
    def __init__(
        self,
        actuator_id: str,
        actuator_type: str,
        initial_state: Any,
        safety_predicate: Optional[Callable[[Any], bool]] = None
    ):
        self.actuator_id = actuator_id
        self.actuator_type = actuator_type
        self.state = initial_state
        self.safety_predicate = safety_predicate or (lambda s: True)
        self.command_history: list = []

    def command(self, new_state: Any, reason: str = "operational_adjustment") -> bool:
        """
        Executes a state transition on the actuator.
        Halts immediately with ActuatorSafetyViolation if safety bounds are exceeded.
        """
        if not self.safety_predicate(new_state):
            raise ActuatorSafetyViolation(
                f"Actuator '{self.actuator_id}' command rejected: State '{new_state}' violates safety bounds."
            )

        old_state = self.state
        self.state = new_state
        entry = {
            "timestamp": time.time(),
            "actuator_id": self.actuator_id,
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason
        }
        self.command_history.append(entry)
        checkpoint(entry, alias=f"actuator_{self.actuator_id}")
        return True


class EdgeAirgapSupervisor:
    """
    Supervises physical environmental continuity for edge nodes:
    manages degraded power states, offline airgap caches, and atomic flush.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.mode = "NORMAL"
        self.brownout_events: int = 0

    def trigger_brownout_protection(self) -> str:
        """Activates emergency low-power preservation and flushes write-ahead memory."""
        self.mode = "AIRGAP_SURVIVAL"
        self.brownout_events += 1
        # Flush and checkpoint emergency state
        receipt = checkpoint(
            {"node": self.node_id, "mode": self.mode, "event": "brownout_protection_activated"},
            alias="emergency_brownout"
        )
        return self.mode

    def restore_nominal_power(self) -> str:
        self.mode = "NORMAL"
        return self.mode
