# Reproduction Guide

## Local verification

```powershell
cd C:\Users\13173\Documents\Codex\2026-08-05\zhe\work\mountainpilot
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/run_demo.py --request "我赶时间，请选择最快路线"
python scripts/run_demo.py --request "我想省电并避开危险道路"
python scripts/run_benchmark.py --output-dir results/latest
```

Acceptance criteria:

1. all tests end in `OK`;
2. the fast and eco requests select different demo routes;
3. the closure scenario excludes edge `A -> D`;
4. benchmark JSON and CSV each contain three scenarios; and
5. no CARLA installation is required for these checks.

## Optional CARLA probe

Install the CARLA Python client matching the separately installed server, start the server, then run
`python scripts/probe_carla.py`. Exit code `0` means connected, `1` means the client loaded but the
server connection failed, and `2` means invalid configuration or a missing Python client.
