"""Shared immutable data structures used by planners and simulators."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot


@dataclass(frozen=True, slots=True)
class Point2D:
    x: float
    y: float

    def distance_to(self, other: Point2D) -> float:
        return hypot(other.x - self.x, other.y - self.y)


@dataclass(frozen=True, slots=True)
class Node:
    node_id: str
    position: Point2D


@dataclass(frozen=True, slots=True)
class Edge:
    source: str
    target: str
    distance_m: float
    speed_limit_mps: float = 13.89
    grade: float = 0.0
    curvature: float = 0.0
    risk: float = 0.0
    blocked: bool = False

    def __post_init__(self) -> None:
        if self.distance_m <= 0:
            raise ValueError("edge distance must be positive")
        if self.speed_limit_mps <= 0:
            raise ValueError("speed limit must be positive")
        if not -0.25 <= self.grade <= 0.25:
            raise ValueError("grade must be expressed as a ratio between -0.25 and 0.25")
        if self.curvature < 0 or self.risk < 0:
            raise ValueError("curvature and risk must be non-negative")


@dataclass(frozen=True, slots=True)
class Route:
    node_ids: tuple[str, ...]
    edges: tuple[Edge, ...]
    total_cost: float
    expanded_nodes: int

    @property
    def distance_m(self) -> float:
        return sum(edge.distance_m for edge in self.edges)

    @property
    def estimated_time_s(self) -> float:
        return sum(edge.distance_m / edge.speed_limit_mps for edge in self.edges)


@dataclass(slots=True)
class VehicleState:
    x: float
    y: float
    yaw_rad: float
    speed_mps: float = 0.0
    acceleration_mps2: float = 0.0
    elapsed_s: float = 0.0
    metadata: dict[str, float | str] = field(default_factory=dict)

    @property
    def position(self) -> Point2D:
        return Point2D(self.x, self.y)
