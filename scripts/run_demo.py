"""Run an end-to-end MountainPilot route-preference and planning demo."""

from __future__ import annotations

import argparse
import json

from mountainpilot.cockpit import interpret_route_request
from mountainpilot.core import build_demo_graph
from mountainpilot.planning import GlobalPlanner, RouteCostModel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", default="帮我选择一条省电而且安全的路线")
    parser.add_argument("--close", nargs=2, metavar=("SOURCE", "TARGET"))
    args = parser.parse_args()

    preference = interpret_route_request(args.request)
    graph = build_demo_graph()
    if args.close:
        graph.set_blocked(args.close[0], args.close[1])
    model = RouteCostModel.for_profile(preference.profile)
    route = GlobalPlanner(graph, model).astar("A", "F")
    payload = {
        "request": preference.request_text,
        "selected_profile": preference.profile.value,
        "safety_preference": preference.avoid_high_risk,
        "explanation": preference.explanation,
        "route": list(route.node_ids),
        "distance_m": round(route.distance_m, 2),
        "estimated_time_s": round(route.estimated_time_s, 2),
        "estimated_energy_wh": round(
            sum(model.estimate_energy_wh(edge) for edge in route.edges), 2
        ),
        "expanded_nodes": route.expanded_nodes,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
