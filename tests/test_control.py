import math
import unittest

from mountainpilot.control import PIDController, PurePursuitController
from mountainpilot.core import Point2D, VehicleState
from mountainpilot.sim import KinematicBicycle


class ControllerTests(unittest.TestCase):
    def test_pid_accelerates_when_below_target(self) -> None:
        self.assertGreater(PIDController().step(10.0, 2.0, 0.1), 0.0)

    def test_pid_rejects_invalid_time_step(self) -> None:
        with self.assertRaisesRegex(ValueError, "dt"):
            PIDController().step(10.0, 2.0, 0.0)

    def test_pure_pursuit_turns_toward_target(self) -> None:
        state = VehicleState(0.0, 0.0, 0.0, speed_mps=5.0)
        controller = PurePursuitController()
        self.assertGreater(controller.steering_angle(state, Point2D(10.0, 5.0)), 0.0)
        self.assertLess(controller.steering_angle(state, Point2D(10.0, -5.0)), 0.0)

    def test_vehicle_model_moves_forward(self) -> None:
        state = VehicleState(0.0, 0.0, 0.0, speed_mps=2.0)
        result = KinematicBicycle().step(state, 1.0, 0.0, 1.0)
        self.assertAlmostEqual(result.speed_mps, 3.0)
        self.assertAlmostEqual(result.x, 2.5)
        self.assertTrue(math.isclose(result.y, 0.0, abs_tol=1e-9))


if __name__ == "__main__":
    unittest.main()
