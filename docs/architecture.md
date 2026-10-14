# Architecture and Safety Boundary

## Module map

- `core`: immutable graph, route, geometry, and mutable vehicle-state data structures.
- `planning`: route weights, simplified energy estimation, Dijkstra, and A*.
- `behavior`: inspectable finite-state decisions above the controllers.
- `control`: PID longitudinal control and Pure Pursuit lateral control.
- `sim`: optional CARLA probe plus a dependency-free kinematic simulator.
- `cockpit`: natural-language route preference to a constrained schema.
- `evaluation`: deterministic planner scenarios and metrics.

## End-to-end data flow

1. `interpret_route_request` maps user text to `fast`, `eco`, or `comfort`.
2. `RouteCostModel` converts edge attributes into a non-negative scalar cost.
3. `GlobalPlanner` searches the directed graph and returns a typed `Route`.
4. `BehaviorPlanner` chooses a high-level state and target speed.
5. PID and Pure Pursuit commands update the offline bicycle model.
6. Evaluation records route, energy, search effort, arrival, acceleration, and jerk metrics.

## Safety decisions

- Natural language never produces actuator commands.
- Empty and oversized cockpit requests are rejected; unknown requests fall back to comfort mode.
- Blocked edges are removed from normal graph expansion.
- Acceleration and steering are clamped inside their respective models.
- CARLA is lazily imported so its absence cannot break offline planning tests.

## Evidence boundary

Unit tests verify software behavior against this small deterministic model. They do not prove road
safety, perception correctness, CARLA compatibility, or real-vehicle energy accuracy. A production
system would require map validation, perception, uncertainty handling, formal safety requirements,
hardware-in-the-loop tests, and vehicle-specific calibration.
