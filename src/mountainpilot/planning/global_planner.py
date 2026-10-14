"""Dijkstra and A* planners sharing one deterministic implementation."""

from __future__ import annotations

import heapq
from collections.abc import Callable
from math import inf

from mountainpilot.core import Edge, RoadGraph, Route

from .costs import RouteCostModel


class GlobalPlanner:
    def __init__(self, graph: RoadGraph, cost_model: RouteCostModel) -> None:
        self.graph = graph
        self.cost_model = cost_model

    def dijkstra(self, start: str, goal: str) -> Route:
        return self._search(start, goal, heuristic=lambda _node: 0.0)

    def astar(self, start: str, goal: str) -> Route:
        goal_position = self.graph.node(goal).position
        min_distance_weight = self.cost_model.weights.distance

        def heuristic(node_id: str) -> float:
            position = self.graph.node(node_id).position
            return position.distance_to(goal_position) * min_distance_weight

        return self._search(start, goal, heuristic=heuristic)

    def _search(self, start: str, goal: str, heuristic: Callable[[str], float]) -> Route:
        self.graph.node(start)
        self.graph.node(goal)
        frontier: list[tuple[float, int, str]] = [(heuristic(start), 0, start)]
        distances: dict[str, float] = {start: 0.0}
        previous: dict[str, tuple[str, Edge]] = {}
        counter = 0
        expanded = 0

        while frontier:
            priority, _order, node_id = heapq.heappop(frontier)
            expected = distances[node_id] + heuristic(node_id)
            if priority > expected + 1e-9:
                continue
            expanded += 1
            if node_id == goal:
                return self._reconstruct(start, goal, previous, distances[goal], expanded)

            for edge in self.graph.neighbors(node_id):
                candidate = distances[node_id] + self.cost_model.edge_cost(edge)
                if candidate < distances.get(edge.target, inf):
                    distances[edge.target] = candidate
                    previous[edge.target] = (node_id, edge)
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (candidate + heuristic(edge.target), counter, edge.target),
                    )

        raise ValueError(f"no route from {start} to {goal}")

    @staticmethod
    def _reconstruct(
        start: str,
        goal: str,
        previous: dict[str, tuple[str, Edge]],
        total_cost: float,
        expanded: int,
    ) -> Route:
        node_ids = [goal]
        edges: list[Edge] = []
        current = goal
        while current != start:
            parent, edge = previous[current]
            node_ids.append(parent)
            edges.append(edge)
            current = parent
        node_ids.reverse()
        edges.reverse()
        return Route(tuple(node_ids), tuple(edges), total_cost, expanded)
