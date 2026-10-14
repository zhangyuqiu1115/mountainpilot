"""A safety-oriented finite-state machine above the motion controllers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BehaviorState(str, Enum):
    DRIVING = "driving"
    FOLLOWING = "following"
    STOPPED = "stopped"
    REPLANNING = "replanning"
    ARRIVED = "arrived"


@dataclass(frozen=True, slots=True)
class BehaviorContext:
    remaining_distance_m: float
    ego_speed_mps: float
    lead_distance_m: float | None = None
    obstacle_distance_m: float | None = None
    route_blocked: bool = False


class BehaviorPlanner:
    def __init__(self, cruise_speed_mps: float = 10.0) -> None:
        if cruise_speed_mps <= 0:
            raise ValueError("cruise speed must be positive")
        self.cruise_speed_mps = cruise_speed_mps
        self.state = BehaviorState.DRIVING

    def update(self, context: BehaviorContext) -> BehaviorState:
        if context.remaining_distance_m <= 1.0 and context.ego_speed_mps <= 0.5:
            self.state = BehaviorState.ARRIVED
        elif context.route_blocked:
            self.state = BehaviorState.REPLANNING
        elif context.obstacle_distance_m is not None and context.obstacle_distance_m < 6.0:
            self.state = BehaviorState.STOPPED
        elif context.lead_distance_m is not None and context.lead_distance_m < 20.0:
            self.state = BehaviorState.FOLLOWING
        else:
            self.state = BehaviorState.DRIVING
        return self.state

    def target_speed(self, context: BehaviorContext) -> float:
        state = self.update(context)
        if state in {BehaviorState.STOPPED, BehaviorState.REPLANNING, BehaviorState.ARRIVED}:
            return 0.0
        if state is BehaviorState.FOLLOWING:
            assert context.lead_distance_m is not None
            return min(self.cruise_speed_mps, max(0.0, (context.lead_distance_m - 6.0) / 1.8))
        return self.cruise_speed_mps
