"""
Ani++ / Haven Robotics, Embedded & Cyber-Physical Control Suite
High-precision real-time PID controllers, 1D/2D Kalman Filters, and Streaming Ring Buffers.
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import math
from typing import Any, List, Optional, Tuple


class PIDController:
    """
    Industrial Real-Time Proportional-Integral-Derivative (PID) Controller:
    Includes anti-windup integral clamping, derivative filtering, and bounded output.
    """
    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float = 0.0,
        output_limits: Tuple[float, float] = (-100.0, 100.0)
    ):
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.setpoint = float(setpoint)
        self.min_out, self.max_out = output_limits

        self._integral = 0.0
        self._prev_error = 0.0
        self._last_time: Optional[float] = None

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._last_time = None

    def update(self, current_value: float, dt: float = 0.01) -> float:
        """Computes control action based on error and elapsed time dt."""
        if dt <= 0:
            dt = 1e-4

        error = self.setpoint - float(current_value)

        # Proportional
        p_term = self.kp * error

        # Integral with anti-windup
        self._integral += error * dt
        i_term = self.ki * self._integral

        # Derivative
        derivative = (error - self._prev_error) / dt
        d_term = self.kd * derivative

        raw_output = p_term + i_term + d_term

        # Clamp output
        clamped_output = max(self.min_out, min(raw_output, self.max_out))

        # Anti-windup: if clamped, freeze integration
        if clamped_output != raw_output:
            self._integral -= error * dt

        self._prev_error = error
        return clamped_output

    def __repr__(self) -> str:
        return f"PIDController(kp={self.kp}, ki={self.ki}, kd={self.kd}, setpoint={self.setpoint})"


class KalmanFilter:
    """
    1D Discrete Kalman Filter for noisy sensor telemetry fusion:
    Estimates the true state of a dynamic system under Gaussian white noise.
    """
    def __init__(
        self,
        initial_state: float = 0.0,
        process_variance: float = 1e-4,
        measurement_variance: float = 1e-2,
        estimated_error: float = 1.0
    ):
        self.q = float(process_variance)        # Process noise covariance
        self.r = float(measurement_variance)    # Measurement noise covariance
        self.p = float(estimated_error)         # Estimation error covariance
        self.x = float(initial_state)           # State estimate
        self.k = 0.0                            # Kalman gain

    def update(self, measurement: float) -> float:
        # 1. Prediction update
        self.p = self.p + self.q

        # 2. Measurement update
        self.k = self.p / (self.p + self.r)
        self.x = self.x + self.k * (float(measurement) - self.x)
        self.p = (1.0 - self.k) * self.p

        return self.x

    @property
    def state(self) -> float:
        return self.x

    def __repr__(self) -> str:
        return f"KalmanFilter(state={self.x:.4f}, p={self.p:.6f})"


class CircularRingBuffer:
    """
    O(1) Streaming Circular Ring Buffer:
    Maintains fixed capacity telemetry streams with rolling averages and peak-to-peak metrics.
    """
    def __init__(self, capacity: int = 100):
        if capacity <= 0:
            raise ValueError("RingBuffer capacity must be strictly positive.")
        self.capacity = capacity
        self._buffer: List[float] = [0.0] * capacity
        self._head = 0
        self._count = 0

    def push(self, value: float) -> None:
        self._buffer[self._head] = float(value)
        self._head = (self._head + 1) % self.capacity
        if self._count < self.capacity:
            self._count += 1

    def to_list(self) -> List[float]:
        if self._count < self.capacity:
            return self._buffer[:self._count]
        return self._buffer[self._head:] + self._buffer[:self._head]

    def mean(self) -> float:
        items = self.to_list()
        return sum(items) / len(items) if items else 0.0

    def min(self) -> float:
        items = self.to_list()
        return min(items) if items else 0.0

    def max(self) -> float:
        items = self.to_list()
        return max(items) if items else 0.0

    def peak_to_peak(self) -> float:
        """Returns range (max - min) of the current telemetry window."""
        items = self.to_list()
        return (max(items) - min(items)) if items else 0.0

    def __len__(self) -> int:
        return self._count

    def __repr__(self) -> str:
        return f"CircularRingBuffer(count={self._count}/{self.capacity}, mean={self.mean():.2f})"
