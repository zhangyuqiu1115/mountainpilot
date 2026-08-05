"""Small, testable boundary for connecting to a CARLA simulator server."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from types import ModuleType
from typing import Any

DEFAULT_CARLA_HOST = "127.0.0.1"
DEFAULT_CARLA_PORT = 2000
DEFAULT_CARLA_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True, slots=True)
class CarlaConnectionConfig:
    """Connection settings for a local or remote CARLA server."""

    host: str = DEFAULT_CARLA_HOST
    port: int = DEFAULT_CARLA_PORT
    timeout_seconds: float = DEFAULT_CARLA_TIMEOUT_SECONDS

    @classmethod
    def from_environment(cls) -> CarlaConnectionConfig:
        """Build a validated configuration from optional environment variables."""

        host = os.getenv("CARLA_HOST", DEFAULT_CARLA_HOST)
        try:
            port = int(os.getenv("CARLA_PORT", str(DEFAULT_CARLA_PORT)))
        except ValueError as exc:
            raise ValueError("CARLA_PORT must be an integer") from exc
        try:
            timeout_seconds = float(
                os.getenv("CARLA_TIMEOUT_SECONDS", str(DEFAULT_CARLA_TIMEOUT_SECONDS))
            )
        except ValueError as exc:
            raise ValueError("CARLA_TIMEOUT_SECONDS must be a number") from exc

        if not host.strip():
            raise ValueError("CARLA_HOST must not be blank")
        if not 1 <= port <= 65535:
            raise ValueError("CARLA_PORT must be between 1 and 65535")
        if timeout_seconds <= 0:
            raise ValueError("CARLA_TIMEOUT_SECONDS must be greater than zero")

        return cls(host=host, port=port, timeout_seconds=timeout_seconds)


@dataclass(frozen=True, slots=True)
class CarlaProbeResult:
    """Serializable result returned by the connection probe."""

    connected: bool
    message: str
    map_name: str | None = None


def _load_carla_module() -> ModuleType:
    try:
        return importlib.import_module("carla")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "CARLA Python client is not installed. Install the client version that matches "
            "the CARLA server before running the simulator probe."
        ) from exc


def probe_carla_connection(
    config: CarlaConnectionConfig,
    *,
    carla_module: Any | None = None,
) -> CarlaProbeResult:
    """Connect to CARLA and return a user-facing health result.

    ``carla_module`` is injectable so CI can validate the integration contract without running
    the simulator.
    """

    module = carla_module if carla_module is not None else _load_carla_module()

    try:
        client = module.Client(config.host, config.port)
        client.set_timeout(config.timeout_seconds)
        world = client.get_world()
        map_name = world.get_map().name
    except Exception as exc:  # CARLA raises several RPC-specific exception types.
        return CarlaProbeResult(
            connected=False,
            message=f"Unable to connect to CARLA at {config.host}:{config.port}: {exc}",
        )

    return CarlaProbeResult(
        connected=True,
        message=f"Connected to CARLA at {config.host}:{config.port}",
        map_name=map_name,
    )
