from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mountainpilot.sim import CarlaConnectionConfig, probe_carla_connection


class _FakeMap:
    name = "Town10HD_Opt"


class _FakeWorld:
    def get_map(self) -> _FakeMap:
        return _FakeMap()


class _FakeClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.timeout: float | None = None

    def set_timeout(self, timeout: float) -> None:
        self.timeout = timeout

    def get_world(self) -> _FakeWorld:
        return _FakeWorld()


class _FakeCarla:
    Client = _FakeClient


class _UnavailableClient(_FakeClient):
    def get_world(self) -> _FakeWorld:
        raise TimeoutError("simulator did not respond")


class _UnavailableCarla:
    Client = _UnavailableClient


class CarlaConnectionConfigTests(unittest.TestCase):
    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = CarlaConnectionConfig.from_environment()

        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 2000)
        self.assertEqual(config.timeout_seconds, 5.0)

    def test_environment_override(self) -> None:
        values = {
            "CARLA_HOST": "carla.internal",
            "CARLA_PORT": "2100",
            "CARLA_TIMEOUT_SECONDS": "2.5",
        }
        with patch.dict(os.environ, values, clear=True):
            config = CarlaConnectionConfig.from_environment()

        self.assertEqual(config.host, "carla.internal")
        self.assertEqual(config.port, 2100)
        self.assertEqual(config.timeout_seconds, 2.5)

    def test_invalid_port_is_rejected(self) -> None:
        with patch.dict(os.environ, {"CARLA_PORT": "70000"}, clear=True):
            with self.assertRaisesRegex(ValueError, "CARLA_PORT"):
                CarlaConnectionConfig.from_environment()


class CarlaProbeTests(unittest.TestCase):
    def test_successful_connection_reports_map(self) -> None:
        result = probe_carla_connection(
            CarlaConnectionConfig(),
            carla_module=_FakeCarla,
        )

        self.assertTrue(result.connected)
        self.assertEqual(result.map_name, "Town10HD_Opt")

    def test_server_failure_is_reported_without_crashing(self) -> None:
        result = probe_carla_connection(
            CarlaConnectionConfig(),
            carla_module=_UnavailableCarla,
        )

        self.assertFalse(result.connected)
        self.assertIn("simulator did not respond", result.message)


if __name__ == "__main__":
    unittest.main()

