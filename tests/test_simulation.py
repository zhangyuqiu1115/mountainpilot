import unittest

from mountainpilot.core import Edge, Node, Point2D, RoadGraph, Route, build_demo_graph
from mountainpilot.planning import DrivingProfile, GlobalPlanner, RouteCostModel
from mountainpilot.sim import OfflineRouteSimulator, SimulationConfig


class OfflineSimulationTests(unittest.TestCase):
    def test_straight_route_reaches_goal_and_stops(self) -> None:
        graph = RoadGraph()
        graph.add_node(Node("start", Point2D(0.0, 0.0)))
        graph.add_node(Node("middle", Point2D(30.0, 0.0)))
        graph.add_node(Node("goal", Point2D(60.0, 0.0)))
        graph.add_edge(Edge("start", "middle", 30.0, 10.0))
        graph.add_edge(Edge("middle", "goal", 30.0, 10.0))
        route = GlobalPlanner(
            graph,
            RouteCostModel.for_profile(DrivingProfile.COMFORT),
        ).astar("start", "goal")
        result = OfflineRouteSimulator(SimulationConfig(maximum_time_s=30.0)).run(graph, route)

        self.assertTrue(result.success)
        self.assertLessEqual(result.arrival_error_m, 2.0)
        self.assertGreater(result.travelled_distance_m, 55.0)
        self.assertGreater(len(result.samples), 10)

    def test_invalid_route_is_rejected(self) -> None:
        graph = RoadGraph()
        graph.add_node(Node("only", Point2D(0.0, 0.0)))
        route = Route(("only",), (), 0.0, 0)
        with self.assertRaisesRegex(ValueError, "at least two"):
            OfflineRouteSimulator().run(graph, route)

    def test_demo_eco_route_completes_closed_loop(self) -> None:
        graph = build_demo_graph()
        route = GlobalPlanner(
            graph,
            RouteCostModel.for_profile(DrivingProfile.ECO),
        ).astar("A", "F")
        result = OfflineRouteSimulator().run(graph, route)
        self.assertTrue(result.success)
        self.assertLess(result.arrival_error_m, 1.0)


if __name__ == "__main__":
    unittest.main()
