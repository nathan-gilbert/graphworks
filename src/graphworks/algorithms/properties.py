"""Graph property queries and structural metrics.

Provides predicate functions (``is_*``) and quantitative metrics (``density``, ``diameter``,
``degree_sequence``, etc.) that inspect a :class:`~graphworks.graph.Graph` without modifying it,
plus :func:`complement`, which builds a new graph.

All functions are pure: they take a graph (and optional parameters) and return a value.  None of
the functions here require numpy.

Conventions
-----------
* A vertex's degree counts every edge incident to it; for directed graphs that is in-degree plus
  out-degree.  A self-loop contributes 2.
* Predicates are vacuously ``True`` on the empty graph.  Metrics that are undefined on the empty
  graph (:func:`min_degree`, :func:`max_degree`, :func:`diameter`) raise :class:`ValueError`.
* Passing a vertex that is not in the graph raises :class:`KeyError`.
"""

from __future__ import annotations

from typing import Final

from ..graph import Graph
from .search import breadth_first_search

DENSITY_CUTOFF: Final[float] = 0.5

# ---------------------------------------------------------------------------
# Degree helpers
# ---------------------------------------------------------------------------


def _degrees(graph: Graph) -> dict[str, int]:
    """Return the degree of every vertex in one pass over the edges.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Mapping of vertex name to degree.
    :rtype: dict[str, int]
    """
    degrees = dict.fromkeys(graph.vertices(), 0)
    for edge in graph.edges():
        degrees[edge.source] += 1
        degrees[edge.target] += 1
    return degrees


def vertex_degree(graph: Graph, vertex: str) -> int:
    """Return the degree of *vertex*.

    For directed graphs this is in-degree plus out-degree.  Self-loops are counted twice.

    :param graph: The graph to inspect.
    :type graph: Graph
    :param vertex: Vertex name.
    :type vertex: str
    :return: Degree of *vertex*.
    :rtype: int
    :raises KeyError: If *vertex* is not in the graph.
    """
    if vertex not in graph:
        msg = f"Vertex {vertex!r} is not in the graph."
        raise KeyError(msg)
    return _degrees(graph)[vertex]


def degree_sequence(graph: Graph) -> list[int]:
    """Return the degree sequence of the graph in non-increasing order.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Sorted list of vertex degrees (highest first).
    :rtype: list[int]
    """
    return sorted(_degrees(graph).values(), reverse=True)


def min_degree(graph: Graph) -> int:
    """Return the minimum vertex degree in the graph.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Minimum degree across all vertices.
    :rtype: int
    :raises ValueError: If the graph has no vertices.
    """
    _require_vertices(graph, "min_degree")
    return min(_degrees(graph).values())


def max_degree(graph: Graph) -> int:
    """Return the maximum vertex degree in the graph.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Maximum degree across all vertices.
    :rtype: int
    :raises ValueError: If the graph has no vertices.
    """
    _require_vertices(graph, "max_degree")
    return max(_degrees(graph).values())


# ---------------------------------------------------------------------------
# Sequence predicates
# ---------------------------------------------------------------------------


def is_degree_sequence(sequence: list[int]) -> bool:
    """Return whether *sequence* is a valid degree sequence.

    A valid degree sequence is non-negative, has an even sum, and is non-increasing.

    :param sequence: Candidate degree sequence.
    :type sequence: list[int]
    :return: ``True`` if *sequence* is a valid degree sequence.
    :rtype: bool
    """
    return (
        all(d >= 0 for d in sequence)
        and sum(sequence) % 2 == 0
        and sequence == sorted(sequence, reverse=True)
    )


def is_erdos_gallai(sequence: list[int]) -> bool:
    """Return whether *sequence* satisfies the Erdős–Gallai theorem.

    A non-increasing sequence of non-negative integers is a valid degree sequence of a simple
    graph if and only if its sum is even and the Erdős–Gallai condition holds for every prefix.

    :param sequence: Candidate degree sequence (need not be sorted).
    :type sequence: list[int]
    :return: ``True`` if *sequence* is graphical per Erdős–Gallai.
    :rtype: bool
    """
    if not sequence:
        return True

    seq = sorted(sequence, reverse=True)
    n = len(seq)

    if sum(seq) % 2 != 0:
        return False

    for k in range(1, n + 1):
        lhs = sum(seq[:k])
        rhs = k * (k - 1) + sum(min(d, k) for d in seq[k:])
        if lhs > rhs:
            return False
    return True


# ---------------------------------------------------------------------------
# Structural predicates
# ---------------------------------------------------------------------------


def is_regular(graph: Graph) -> bool:
    """Return whether every vertex in the graph has the same degree.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is regular (all degrees equal).
    :rtype: bool
    """
    return len(set(_degrees(graph).values())) <= 1


def is_simple(graph: Graph) -> bool:
    """Return whether the graph contains no self-loops.

    :class:`~graphworks.graph.Graph` cannot hold parallel edges, so a loop-free graph is simple.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if no vertex has an edge to itself.
    :rtype: bool
    """
    return not any(edge.is_self_loop() for edge in graph.edges())


def is_connected(graph: Graph) -> bool:
    """Return whether the graph is connected.

    Directed graphs are tested for *weak* connectivity (edge directions are ignored).

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if every vertex is reachable from every other, ignoring direction.
    :rtype: bool
    """
    verts = graph.vertices()
    if not verts:
        return True
    underlying = Graph()
    for v in verts:
        underlying.add_vertex(v)
    for edge in graph.edges():
        underlying.add_edge(edge.source, edge.target)
    return len(breadth_first_search(underlying, verts[0])) == len(verts)


def is_complete(graph: Graph) -> bool:
    """Return whether the graph is complete.

    A complete graph has an edge from every vertex to every other vertex and no self-loops.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is complete.
    :rtype: bool
    """
    verts = set(graph.vertices())
    return all(set(graph[v]) == verts - {v} for v in verts)


def is_sparse(graph: Graph) -> bool:
    """Return whether the graph is sparse (density below ``DENSITY_CUTOFF``).

    Always the opposite of :func:`is_dense`.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is sparse.
    :rtype: bool
    """
    return not is_dense(graph)


def is_dense(graph: Graph) -> bool:
    """Return whether the graph is dense (density ≥ ``DENSITY_CUTOFF``).

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: ``True`` if the graph is dense.
    :rtype: bool
    """
    return density(graph) >= DENSITY_CUTOFF


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def density(graph: Graph) -> float:
    """Return the density of the graph.

    Density is the number of edges divided by the maximum possible: ``|V|(|V|-1)`` for directed
    graphs and ``|V|(|V|-1)/2`` for undirected graphs.  Self-loops are not counted.  Returns
    ``0.0`` for graphs with fewer than two vertices.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Density in the range ``[0.0, 1.0]``.
    :rtype: float
    """
    v_count = graph.order
    if v_count < 2:  # noqa: PLR2004
        return 0.0
    e_count = sum(1 for edge in graph.edges() if not edge.is_self_loop())
    max_edges = v_count * (v_count - 1)
    if not graph.directed:
        max_edges //= 2
    return e_count / max_edges


def diameter(graph: Graph) -> int:
    """Return the diameter of the graph.

    The diameter is the greatest shortest-path distance (in edges) between any ordered pair of
    vertices, computed with one breadth-first search per vertex.

    :param graph: The graph to inspect.
    :type graph: Graph
    :return: Diameter (number of edges on the longest shortest path).
    :rtype: int
    :raises ValueError: If the graph is empty, or if some vertex cannot reach another (the
        diameter is infinite).
    """
    _require_vertices(graph, "diameter")
    longest = 0
    for start in graph.vertices():
        dist = {start: 0}
        frontier = [start]
        while frontier:
            nxt: list[str] = []
            for u in frontier:
                for w in graph[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        nxt.append(w)
            frontier = nxt
        if len(dist) != graph.order:
            msg = "diameter is infinite: the graph is not (strongly) connected."
            raise ValueError(msg)
        longest = max(longest, *dist.values())
    return longest


# ---------------------------------------------------------------------------
# Derived graphs
# ---------------------------------------------------------------------------


def complement(graph: Graph) -> Graph:
    """Return the complement graph of *graph*.

    The complement has the same vertices (names, labels, and attributes preserved) and the same
    :attr:`~graphworks.graph.Graph.directed` flag, and contains exactly the edges between
    distinct vertices that are *not* in *graph*.  No self-loops are added.

    :param graph: The source graph.
    :type graph: Graph
    :return: Complement graph.
    :rtype: Graph
    """
    result = Graph(f"{graph.label} complement".strip(), directed=graph.directed)
    for name in graph:
        vertex = graph.vertex(name)
        if vertex is not None:
            result.add_vertex(vertex)
    for u in graph:
        for v in graph:
            if u != v and graph.edge(u, v) is None and result.edge(u, v) is None:
                result.add_edge(u, v)
    return result


def _require_vertices(graph: Graph, name: str) -> None:
    """Raise :class:`ValueError` if *graph* is empty.

    :param graph: The graph to inspect.
    :type graph: Graph
    :param name: Name of the calling function, for the error message.
    :type name: str
    :return: Nothing.
    :rtype: None
    :raises ValueError: If the graph has no vertices.
    """
    if graph.order == 0:
        msg = f"{name}() is undefined for a graph with no vertices."
        raise ValueError(msg)
