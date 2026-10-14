import unittest

from mountainpilot.evaluation import run_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_benchmark_contains_three_named_scenarios(self) -> None:
        records = run_benchmark()
        self.assertEqual(
            {record.scenario for record in records},
            {"fastest_route", "energy_aware_route", "road_closure_replan"},
        )

    def test_road_closure_changes_eco_route(self) -> None:
        records = {record.scenario: record for record in run_benchmark()}
        self.assertNotEqual(
            records["energy_aware_route"].route,
            records["road_closure_replan"].route,
        )

    def test_all_metrics_are_positive(self) -> None:
        for record in run_benchmark():
            self.assertGreater(record.distance_m, 0.0)
            self.assertGreater(record.estimated_time_s, 0.0)
            self.assertGreater(record.estimated_energy_wh, 0.0)


if __name__ == "__main__":
    unittest.main()
