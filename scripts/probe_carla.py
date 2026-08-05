"""Probe the configured CARLA simulator and print a concise health result."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict

from mountainpilot.sim import CarlaConnectionConfig, probe_carla_connection


def main() -> int:
    try:
        config = CarlaConnectionConfig.from_environment()
        result = probe_carla_connection(config)
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"connected": False, "message": str(exc)}, indent=2))
        return 2

    print(json.dumps(asdict(result), indent=2))
    return 0 if result.connected else 1


if __name__ == "__main__":
    sys.exit(main())

