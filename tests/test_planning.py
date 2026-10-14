from __future__ import annotations

import unittest

from mountainpilot.core import Edge, Node, Point2D, RoadGraph, build_demo_graph
from mountainpilot.planning import DrivingProfile, GlobalPlanner, RouteCostModel


class RoadGraphTests(unittest.TestCase):
    def test_blocked_edge_is_removed_from_neighbors(self) -> None:
        graph = build_demo_graph()
        graph.set_blocked("B", "C")
        self.assertNotIn("C", {edge.target for edge in graph.neighbors("B")})
        self.assertIn("C", {edge.target for edge in graph.neighbors("B", include_blocked=True)})

    def test_nearest_node(self) -> None:
        graph = build_demo_graph()
        self.assertEqual(graph.nearest_node(Point2D(3.0, 2.0)).node_id, "A")


class CostModelTests(unittest.TestCase):
    def test_uphill_uses_more_energy_than_flat(self) -> None:
        model = RouteCostModel.for_profile(DrivingProfile.ECO)
        flat = Edge("A", "B", 100.0, grade=0.0)
        uphill = Edge("A", "B", 100.0, grade=0.1)
        self.assertGreater(model.estimate_energy_wh(uphill), model.estimate_energy_wh(flat))

    def test_invalid_edge_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "distance"):
            Edge("A", "B", 0.0)


class GlobalPlannerTests(unittest.TestCase):
    def test_dijkstra_and_astar_find_equal_cost(self) -> None:
        graph = build_demo_graph()
        planner = GlobalPlanner(graph, RouteCostModel.for_profile(DrivingProfile.FAST))
        dijkstra = planner.dijkstra("A", "F")
        astar = planner.astar("A", "F")
        self.assertAlmostEqual(dijkstra.total_cost, astar.total_cost)
        self.assertEqual(dijkstra.node_ids, astar.node_ids)

    def test_eco_profile_avoids_steep_route(self) -> None:
        graph = build_demo_graph()
        planner = GlobalPlanner(graph, RouteCostModel.for_profile(DrivingProfile.ECO))
        route = planner.astar("A", "F")
        self.assertEqual(route.node_ids, ("A", "D", "E", "F"))

    def test_fast_profile_prefers_short_route(self) -> None:
        graph = build_demo_graph()
        planner = GlobalPlanner(graph, RouteCostModel.for_profile(DrivingProfile.FAST))
        self.assertEqual(planner.astar("A", "F").node_ids, ("A", "B", "C", "F"))

    def test_closure_triggers_alternative_route(self) -> None:
        graph = build_demo_graph()
        graph.set_blocked("A", "D")
        planner = GlobalPlanner(graph, RouteCostModel.for_profile(DrivingProfile.ECO))
        route = planner.astar("A", "F")
        self.assertNotEqual(route.node_ids[:2], ("A", "D"))

    def test_disconnected_graph_raises_clear_error(self) -> None:
        graph = RoadGraph()
        graph.add_node(Node("A", Point2D(0.0, 0.0)))
        graph.add_node(Node("B", Point2D(1.0, 0.0)))
        planner = GlobalPlanner(graph, RouteCostModel.for_profile(DrivingProfile.FAST))
        with self.assertRaisesRegex(ValueError, "no route"):
            planner.astar("A", "B")


if __name__ == "__main__":
    unittest.main()
