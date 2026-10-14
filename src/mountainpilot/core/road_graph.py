"""Small directed road graph with explicit blocked-edge support."""

from __future__ import annotations

from dataclasses import replace

from .models import Edge, Node, Point2D


class RoadGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._adjacency: dict[str, dict[str, Edge]] = {}

    @property
    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._nodes.values())

    def add_node(self, node: Node) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node: {node.node_id}")
        self._nodes[node.node_id] = node
        self._adjacency[node.node_id] = {}

    def add_edge(self, edge: Edge, *, bidirectional: bool = False) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise KeyError("both edge endpoints must exist")
        self._adjacency[edge.source][edge.target] = edge
        if bidirectional:
            reverse = replace(edge, source=edge.target, target=edge.source, grade=-edge.grade)
            self._adjacency[reverse.source][reverse.target] = reverse

    def node(self, node_id: str) -> Node:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown node: {node_id}") from exc

    def edge(self, source: str, target: str) -> Edge:
        try:
            return self._adjacency[source][target]
        except KeyError as exc:
            raise KeyError(f"unknown edge: {source}->{target}") from exc

    def neighbors(self, node_id: str, *, include_blocked: bool = False) -> tuple[Edge, ...]:
        self.node(node_id)
        edges = self._adjacency[node_id].values()
        if include_blocked:
            return tuple(edges)
        return tuple(edge for edge in edges if not edge.blocked)

    def set_blocked(self, source: str, target: str, blocked: bool = True) -> None:
        edge = self.edge(source, target)
        self._adjacency[source][target] = replace(edge, blocked=blocked)

    def nearest_node(self, position: Point2D) -> Node:
        if not self._nodes:
            raise ValueError("cannot query an empty graph")
        return min(self._nodes.values(), key=lambda node: node.position.distance_to(position))


def build_demo_graph() -> RoadGraph:
    """Build a small urban graph with short/steep and long/flat alternatives."""

    graph = RoadGraph()
    for node in (
        Node("A", Point2D(0.0, 0.0)),
        Node("B", Point2D(40.0, 0.0)),
        Node("C", Point2D(80.0, 10.0)),
        Node("D", Point2D(40.0, 35.0)),
        Node("E", Point2D(80.0, 35.0)),
        Node("F", Point2D(120.0, 10.0)),
    ):
        graph.add_node(node)

    # Shorter but steep/curvy route: A-B-C-F.
    graph.add_edge(Edge("A", "B", 40.0, 13.0, grade=0.01, curvature=0.01), bidirectional=True)
    graph.add_edge(Edge("B", "C", 42.0, 14.0, grade=0.12, curvature=0.05), bidirectional=True)
    graph.add_edge(Edge("C", "F", 40.0, 13.0, grade=-0.03, curvature=0.02), bidirectional=True)

    # Longer, flatter and smoother route: A-D-E-F.
    graph.add_edge(Edge("A", "D", 54.0, 14.0, grade=0.02, curvature=0.01), bidirectional=True)
    graph.add_edge(Edge("D", "E", 40.0, 15.0, grade=0.01, curvature=0.005), bidirectional=True)
    graph.add_edge(Edge("E", "F", 47.0, 14.0, grade=-0.01, curvature=0.01), bidirectional=True)

    # Cross-links make road-closure replanning possible.
    graph.add_edge(Edge("B", "D", 35.0, 9.0, grade=0.04, curvature=0.08, risk=0.1), bidirectional=True)
    graph.add_edge(Edge("C", "E", 27.0, 10.0, grade=-0.02, curvature=0.04), bidirectional=True)
    return graph
