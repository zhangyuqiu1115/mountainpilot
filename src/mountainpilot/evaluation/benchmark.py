"""Three deterministic scenarios covering routing trade-offs and replanning."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from mountainpilot.core import build_demo_graph
from mountainpilot.planning import DrivingProfile, GlobalPlanner, RouteCostModel


@dataclass(frozen=True, slots=True)
class BenchmarkRecord:
    scenario: str
    profile: str
    route: str
    distance_m: float
    estimated_time_s: float
    estimated_energy_wh: float
    planner_cost: float
    expanded_nodes: int

    def as_dict(self) -> dict[str, str | float | int]:
        return asdict(self)


def _evaluate(scenario: str, profile: DrivingProfile, blocked: tuple[tuple[str, str], ...] = ()) -> BenchmarkRecord:
    graph = build_demo_graph()
    for source, target in blocked:
        graph.set_blocked(source, target)
    cost_model = RouteCostModel.for_profile(profile)
    route = GlobalPlanner(graph, cost_model).astar("A", "F")
    energy = sum(cost_model.estimate_energy_wh(edge) for edge in route.edges)
    return BenchmarkRecord(
        scenario=scenario,
        profile=profile.value,
        route=" -> ".join(route.node_ids),
        distance_m=round(route.distance_m, 2),
        estimated_time_s=round(route.estimated_time_s, 2),
        estimated_energy_wh=round(energy, 2),
        planner_cost=round(route.total_cost, 2),
        expanded_nodes=route.expanded_nodes,
    )


def run_benchmark() -> tuple[BenchmarkRecord, ...]:
    return (
        _evaluate("fastest_route", DrivingProfile.FAST),
        _evaluate("energy_aware_route", DrivingProfile.ECO),
        _evaluate("road_closure_replan", DrivingProfile.ECO, (("A", "D"),)),
    )
