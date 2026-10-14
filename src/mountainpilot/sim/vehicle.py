"""Kinematic bicycle model used when a CARLA server is unavailable."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, tan

from mountainpilot.core import VehicleState


@dataclass(frozen=True, slots=True)
class KinematicBicycle:
    wheelbase_m: float = 2.85
    maximum_acceleration_mps2: float = 2.5
    maximum_deceleration_mps2: float = 4.5

    def step(
        self,
        state: VehicleState,
        acceleration_mps2: float,
        steering_rad: float,
        dt: float,
    ) -> VehicleState:
        if dt <= 0:
            raise ValueError("dt must be positive")
        acceleration = max(
            -self.maximum_deceleration_mps2,
            min(acceleration_mps2, self.maximum_acceleration_mps2),
        )
        speed = max(0.0, state.speed_mps + acceleration * dt)
        average_speed = 0.5 * (state.speed_mps + speed)
        yaw_rate = average_speed * tan(steering_rad) / self.wheelbase_m
        yaw = state.yaw_rad + yaw_rate * dt
        return VehicleState(
            x=state.x + average_speed * cos(yaw) * dt,
            y=state.y + average_speed * sin(yaw) * dt,
            yaw_rad=yaw,
            speed_mps=speed,
            acceleration_mps2=acceleration,
            elapsed_s=state.elapsed_s + dt,
            metadata=dict(state.metadata),
        )
