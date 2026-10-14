# Day 05 - A* Global Planner

## Objective
Reduce search work while preserving the best route under the configured cost.

## Delivered
Added Euclidean-distance A* with stale-frontier filtering and deterministic tie ordering.

## Verification
The A* and Dijkstra route/cost equality test passes; disconnected graphs raise a clear error.

## Next
Expose route reconstruction and metrics.
