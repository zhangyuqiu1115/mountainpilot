# Day 01 - Repository and CARLA Connection Probe

## Goal

Create an auditable project foundation and a small CARLA connection boundary that can be tested
without installing the simulator in continuous integration.

## Completed

- Created the Python package and repository structure.
- Added a typed CARLA connection configuration loaded from environment variables.
- Added a connection probe that reports success, missing dependency, and unavailable server states.
- Added dependency-free unit tests using a fake CARLA module.
- Added GitHub Actions CI and a 30-day delivery roadmap.
- Added repository rules for daily devlogs, test evidence, and annotated Git tags.

## Technical decisions

- CARLA is imported lazily so planner tests and CI do not require the large simulator runtime.
- Connection logic accepts an injected module, which keeps tests deterministic.
- The initial implementation uses only the Python standard library. Simulator, plotting, and AI
  dependencies will be introduced only when their modules are implemented.

## Verification

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected result: all Day 01 unit tests pass.

The first test run exposed a Python `dataclass(slots=True)` issue: accessing field defaults through
the class inside `from_environment` returned slot descriptors. Defaults were moved to explicit
module constants, invalid numeric environment values now receive targeted validation messages,
and the full test suite was rerun after the fix.

The local workstation does not currently provide a verified running CARLA server, so successful
simulator connectivity remains the first external-environment check. The code distinguishes this
from a source-code test failure.

## Risks

- The CARLA server and Python client must use compatible versions.
- CARLA support for the workstation's Python version must be checked before Day 02.

## Next

Install or locate a compatible CARLA runtime, spawn an ego vehicle, and record structured vehicle
state for Day 02.
