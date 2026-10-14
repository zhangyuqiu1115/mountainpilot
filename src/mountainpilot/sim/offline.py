"""Closed-loop route simulation that runs with only the Python standard library."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import atan2, sqrt

from mountainpilot.behavior import BehaviorContext, BehaviorPlanner
from mountainpilot.control import PIDController, PurePursuitController
from mountainpilot.core import RoadGraph, Route, VehicleState

from .vehicle import KinematicBicycle


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    dt_s: float = 0.1
    cruise_speed_mps: float = 10.0
    waypoint_tolerance_m: float = 2.5
    maximum_time_s: float = 180.0
    comfortable_deceleration_mps2: float = 2.2


@dataclass(frozen=True, slots=True)
class SimulationSample:
    time_s: float
    x: float
    y: float
    speed_mps: float
    acceleration_mps2: float
    steering_rad: float
    target_node: str
    behavior: str


@dataclass(frozen=True, slots=True)
class SimulationResult:
    success: bool
    samples: tuple[SimulationSample, ...]
    duration_s: float
    travelled_distance_m: float
    arrival_error_m: float
    maximum_abs_acceleration_mps2: float
    maximum_abs_jerk_mps3: float

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["samples"] = [asdict(sample) for sample in self.samples]
        return payload


class OfflineRouteSimulator:
    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        if self.config.dt_s <= 0 or self.config.maximum_time_s <= 0:
            raise ValueError("simulation time settings must be positive")

    def run(self, graph: RoadGraph, route: Route) -> SimulationResult:
        if len(route.node_ids) < 2:
            raise ValueError("route must contain at least two nodes")
        start = graph.node(route.node_ids[0]).position
        first_target = graph.node(route.node_ids[1]).position
        state = VehicleState(
            x=start.x,
            y=start.y,
            yaw_rad=atan2(first_target.y - start.y, first_target.x - start.x),
        )
        vehicle = KinematicBicycle()
        longitudinal = PIDController()
        lateral = PurePursuitController()
        behavior = BehaviorPlanner(self.config.cruise_speed_mps)
        target_index = 1
        samples: list[SimulationSample] = []
        travelled = 0.0
        previous_acceleration = 0.0
        maximum_jerk = 0.0
        goal_reached = False

        while state.elapsed_s < self.config.maximum_time_s:
            target_id = route.node_ids[target_index]
            target = graph.node(target_id).position
            distance = state.position.distance_to(target)
            if distance <= self.config.waypoint_tolerance_m and target_index < len(route.node_ids) - 1:
                target_index += 1
                target_id = route.node_ids[target_index]
                target = graph.node(target_id).position
                distance = state.position.distance_to(target)

            final_target = target_index == len(route.node_ids) - 1
            if final_target and distance <= 1.0:
                goal_reached = True
            stopping_speed = sqrt(
                max(0.0, 2.0 * self.config.comfortable_deceleration_mps2 * distance)
            )
            context = BehaviorContext(
                remaining_distance_m=distance if final_target else distance + 10.0,
                ego_speed_mps=state.speed_mps,
            )
            target_speed = behavior.target_speed(context)
            if final_target:
                target_speed = min(target_speed, stopping_speed)
            acceleration = longitudinal.step(target_speed, state.speed_mps, self.config.dt_s)
            if goal_reached and state.speed_mps > 0.0:
                acceleration = -self.config.comfortable_deceleration_mps2
            elif final_target and state.speed_mps > stopping_speed:
                acceleration = min(acceleration, -self.config.comfortable_deceleration_mps2)
            steering = lateral.steering_angle(state, target)
            next_state = vehicle.step(state, acceleration, steering, self.config.dt_s)
            travelled += state.position.distance_to(next_state.position)
            jerk = abs(next_state.acceleration_mps2 - previous_acceleration) / self.config.dt_s
            maximum_jerk = max(maximum_jerk, jerk)
            previous_acceleration = next_state.acceleration_mps2
            samples.append(
                SimulationSample(
                    time_s=round(next_state.elapsed_s, 3),
                    x=next_state.x,
                    y=next_state.y,
                    speed_mps=next_state.speed_mps,
                    acceleration_mps2=next_state.acceleration_mps2,
                    steering_rad=steering,
                    target_node=target_id,
                    behavior=behavior.state.value,
                )
            )
            state = next_state
            if goal_reached and state.speed_mps <= 0.5:
                break

        goal = graph.node(route.node_ids[-1]).position
        arrival_error = state.position.distance_to(goal)
        success = arrival_error <= 2.0 and state.speed_mps <= 0.75
        return SimulationResult(
            success=success,
            samples=tuple(samples),
            duration_s=state.elapsed_s,
            travelled_distance_m=travelled,
            arrival_error_m=arrival_error,
            maximum_abs_acceleration_mps2=max(
                (abs(sample.acceleration_mps2) for sample in samples), default=0.0
            ),
            maximum_abs_jerk_mps3=maximum_jerk,
        )
