import unittest

from mountainpilot.behavior import BehaviorContext, BehaviorPlanner, BehaviorState


class BehaviorPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = BehaviorPlanner(cruise_speed_mps=10.0)

    def test_normal_driving(self) -> None:
        context = BehaviorContext(100.0, 5.0)
        self.assertEqual(self.planner.update(context), BehaviorState.DRIVING)
        self.assertEqual(self.planner.target_speed(context), 10.0)

    def test_close_obstacle_has_priority(self) -> None:
        context = BehaviorContext(100.0, 5.0, lead_distance_m=10.0, obstacle_distance_m=3.0)
        self.assertEqual(self.planner.update(context), BehaviorState.STOPPED)

    def test_blocked_route_requests_replanning(self) -> None:
        context = BehaviorContext(100.0, 5.0, route_blocked=True)
        self.assertEqual(self.planner.update(context), BehaviorState.REPLANNING)

    def test_following_reduces_speed(self) -> None:
        context = BehaviorContext(100.0, 5.0, lead_distance_m=12.0)
        self.assertEqual(self.planner.update(context), BehaviorState.FOLLOWING)
        self.assertLess(self.planner.target_speed(context), 10.0)


if __name__ == "__main__":
    unittest.main()
