# MountainPilot Benchmark Report

Generated from the deterministic demo graph with `scripts/run_benchmark.py`.

| Scenario | Profile | Route | Distance (m) | Time (s) | Energy (Wh) | Expanded |
|---|---|---|---:|---:|---:|---:|
| Fast profile | fast | A-B-C-F | 122.00 | 9.15 | 44.92 | 4 |
| Energy-aware | eco | A-D-E-F | 141.00 | 9.88 | 23.16 | 5 |
| A-D road closure | eco | A-B-D-E-F | 162.00 | 12.99 | 29.49 | 5 |

## Interpretation

The fast profile selects the shorter and quicker route, accepting a steep edge and approximately
94% more estimated energy than the eco route. The eco profile selects a longer, flatter alternative.
When its first edge is closed, the planner excludes that edge and returns a valid detour.

These values are outputs of a simplified software model, not measured production-vehicle data.
