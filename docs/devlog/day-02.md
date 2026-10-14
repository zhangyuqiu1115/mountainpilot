# Day 02 - Typed Domain Models

## Objective
Define explicit geometry, road, route, and vehicle-state contracts.

## Delivered
Added `Point2D`, `Node`, `Edge`, `Route`, and `VehicleState` dataclasses in `core/models.py`.

## Verification
Invalid edge distances and grades are rejected; downstream planner tests construct typed routes.

## Next
Store the models in a directed road graph.
