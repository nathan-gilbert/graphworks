"""Implementation of graph edge between 2 vertices."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Edge:
    """Implementation of graph edge between 2 vertices.

    An undirected edge is a line. A directed edge is an arc or arrow. Supports weighted (float)
    edges.
    """

    vertex1: str
    vertex2: str
    directed: bool = False
    weight: float | None = None

    def has_weight(self) -> bool:
        """Returns ``True`` if the edge has a ``weight`` attribute.

        :return: ``True`` if the edge has a ``weight`` attribute, otherwise ``False``.
        :rtype: bool
        """
        return self.weight is not None
