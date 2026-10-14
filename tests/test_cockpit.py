import unittest

from mountainpilot.cockpit import interpret_route_request
from mountainpilot.planning import DrivingProfile


class CockpitPreferenceTests(unittest.TestCase):
    def test_chinese_energy_request_selects_eco(self) -> None:
        result = interpret_route_request("帮我找一条省电而且安全的路线")
        self.assertEqual(result.profile, DrivingProfile.ECO)
        self.assertTrue(result.avoid_high_risk)

    def test_fast_request_selects_fast(self) -> None:
        self.assertEqual(interpret_route_request("I am in a hurry, choose fast").profile, DrivingProfile.FAST)

    def test_unknown_request_uses_safe_default(self) -> None:
        self.assertEqual(interpret_route_request("去目的地").profile, DrivingProfile.COMFORT)

    def test_empty_and_oversized_requests_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            interpret_route_request("  ")
        with self.assertRaisesRegex(ValueError, "200"):
            interpret_route_request("a" * 201)


if __name__ == "__main__":
    unittest.main()
