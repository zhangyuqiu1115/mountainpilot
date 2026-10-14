"""Small, deterministic controllers suitable for simulation demonstrations."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, pi, sin

from mountainpilot.core import Point2D, VehicleState


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


@dataclass(slots=True)
class PIDController:
    kp: float = 0.8
    ki: float = 0.05
    kd: float = 0.08
    integral_limit: float = 10.0
    _integral: float = 0.0
    _previous_error: float | None = None

    def reset(self) -> None:
        self._integral = 0.0
        self._previous_error = None

    def step(self, target: float, measured: float, dt: float) -> float:
        if dt <= 0:
            raise ValueError("dt must be positive")
        error = target - measured
        self._integral = clamp(
            self._integral + error * dt,
            -self.integral_limit,
            self.integral_limit,
        )
        derivative = 0.0
        if self._previous_error is not None:
            derivative = (error - self._previous_error) / dt
        self._previous_error = error
        return self.kp * error + self.ki * self._integral + self.kd * derivative


@dataclass(frozen=True, slots=True)
class PurePursuitController:
    wheelbase_m: float = 2.85
    maximum_steering_rad: float = 0.55

    def steering_angle(self, state: VehicleState, target: Point2D) -> float:
        dx = target.x - state.x
        dy = target.y - state.y
        lookahead = max((dx * dx + dy * dy) ** 0.5, 0.1)
        heading_to_target = atan2(dy, dx)
        alpha = (heading_to_target - state.yaw_rad + pi) % (2 * pi) - pi
        steering = atan2(2.0 * self.wheelbase_m * sin(alpha), lookahead)
        return clamp(steering, -self.maximum_steering_rad, self.maximum_steering_rad)
