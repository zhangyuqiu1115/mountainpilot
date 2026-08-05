# MountainPilot

MountainPilot is a 30-day portfolio project for energy-aware route planning and
closed-loop autonomous-driving simulation in complex urban environments. It is
designed around software engineering, simulation testing, and safe AI-assisted
route preference interpretation.

> Safety notice: this project is for closed-loop simulation and education only.
> It must not be used to control a real vehicle.

## Project goals

- Extract a navigable road graph from CARLA.
- Compare Dijkstra, A*, and energy-aware A* global planners.
- Support fast, eco, and comfort route preferences.
- Add behavior planning, local trajectory planning, and closed-loop control.
- Validate safety, efficiency, comfort, and estimated energy use with repeatable scenarios.
- Interpret cockpit route preferences through a validated AI boundary without putting an LLM
  in the vehicle-control safety loop.

## 30-day build progress

| Day | Module | Status | Evidence |
|---:|---|---|---|
| 01 | Repository and CARLA connection probe | Complete | [Devlog](docs/devlog/day-01.md) |
| 02 | Ego vehicle and state logging | Planned | - |
| 03 | CARLA waypoint graph | Planned | - |
| 04 | Dijkstra baseline | Planned | - |
| 05 | A* global planner | Planned | - |

The remaining daily milestones are tracked in [the 30-day roadmap](docs/roadmap.md).

## Day 01 quick start

MountainPilot supports Python 3.10 or newer. The repository can be tested without CARLA.

```powershell
python -m unittest discover -s tests -v
```

To probe a running local CARLA server, first install the Python client that matches your CARLA
server version, start CARLA, and run:

```powershell
$env:PYTHONPATH="src"
python scripts/probe_carla.py
```

Optional environment variables:

```text
CARLA_HOST=127.0.0.1
CARLA_PORT=2000
CARLA_TIMEOUT_SECONDS=5.0
```

The probe exits with a clear message when the CARLA Python package or server is unavailable.

## Repository structure

```text
mountainpilot/
|-- config/                 # Versioned, non-secret configuration
|-- docs/
|   |-- devlog/             # One auditable development log per day
|   `-- roadmap.md
|-- results/                # Daily benchmark outputs and figures
|-- scripts/                # Runnable entry points
|-- src/mountainpilot/      # Production source code
|-- tests/                  # Unit and later scenario tests
`-- .github/workflows/      # Continuous integration
```

## Development evidence policy

Every project day must contain:

1. a meaningful code or documentation change;
2. a test or reproducible run result;
3. `docs/devlog/day-XX.md`;
4. an updated progress table; and
5. an annotated `day-XX` Git tag.

Empty commits do not count as progress. A blocked day must instead preserve a reproducible
failure, investigation notes, and a next action.

