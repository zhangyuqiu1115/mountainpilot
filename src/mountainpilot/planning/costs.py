"""Energy-aware route cost model for electric vehicles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from mountainpilot.core import Edge


class DrivingProfile(str, Enum):
    FAST = "fast"
    ECO = "eco"
    COMFORT = "comfort"


@dataclass(frozen=True, slots=True)
class RouteWeights:
    distance: float
    time: float
    energy: float
    risk: float
    curvature: float

    def __post_init__(self) -> None:
        values = (self.distance, self.time, self.energy, self.risk, self.curvature)
        if any(value < 0 for value in values):
            raise ValueError("route weights must be non-negative")
        if sum(values) == 0:
            raise ValueError("at least one route weight must be positive")

    @classmethod
    def for_profile(cls, profile: DrivingProfile) -> RouteWeights:
        if profile is DrivingProfile.FAST:
            return cls(distance=0.5, time=0.3, energy=0.01, risk=0.2, curvature=0.03)
        if profile is DrivingProfile.ECO:
            return cls(distance=0.1, time=0.15, energy=1.0, risk=0.6, curvature=0.2)
        return cls(distance=0.1, time=0.2, energy=0.25, risk=0.8, curvature=1.0)


@dataclass(frozen=True, slots=True)
class RouteCostModel:
    weights: RouteWeights
    vehicle_mass_kg: float = 2200.0
    rolling_resistance: float = 0.012
    drag_area: float = 0.75
    drivetrain_efficiency: float = 0.9
    recuperation_efficiency: float = 0.55

    @classmethod
    def for_profile(cls, profile: DrivingProfile) -> RouteCostModel:
        return cls(RouteWeights.for_profile(profile))

    def estimate_energy_wh(self, edge: Edge) -> float:
        """Estimate traction energy, including limited downhill recuperation."""

        gravity = 9.81
        air_density = 1.225
        speed = edge.speed_limit_mps
        rolling_j = self.vehicle_mass_kg * gravity * self.rolling_resistance * edge.distance_m
        aero_j = 0.5 * air_density * self.drag_area * speed**2 * edge.distance_m
        grade_j = self.vehicle_mass_kg * gravity * edge.grade * edge.distance_m
        base_j = rolling_j + aero_j
        if grade_j >= 0:
            total_j = (base_j + grade_j) / self.drivetrain_efficiency
        else:
            total_j = max(0.0, base_j + grade_j * self.recuperation_efficiency)
        return total_j / 3600.0

    def edge_cost(self, edge: Edge) -> float:
        time_s = edge.distance_m / edge.speed_limit_mps
        energy_wh = self.estimate_energy_wh(edge)
        w = self.weights
        return (
            w.distance * edge.distance_m
            + w.time * time_s
            + w.energy * energy_wh
            + w.risk * edge.risk * 100.0
            + w.curvature * edge.curvature * edge.distance_m * 10.0
        )
