"""Core graph data structure for the graphworks library.

Provides :class:`Graph`, which stores graphs internally using first-class
:class:`~graphworks.vertex.Vertex` and :class:`~graphworks.edge.Edge` objects in a dual-index
adjacency structure:

* ``_vertices``: ``dict[str, Vertex]`` — O(1) lookup by name.
* ``_adj``: ``dict[str, dict[str, Edge]]`` — ``_adj[u][v]`` gives the
  :class:`~graphworks.edge.Edge` from *u* to *v* in O(1).

The adjacency matrix interface uses only stdlib types — no numpy required. Optional numpy interop
is available through :mod:`graphworks.numpy_compat`.

Construction
------------
A :class:`Graph` can be built from:

* a JSON file path (``input_file``),
* a JSON string (``input_graph``),
* a stdlib adjacency matrix (``input_matrix``), or
* programmatically via :meth:`add_vertex` / :meth:`add_edge`.

For numpy ``ndarray`` input, convert first with :func:`graphworks.numpy_compat.ndarray_to_matrix`.

Example::

    >>> import json
    >>> from graphworks.graph import Graph  # noqa
    ...
    >>> data = {"label": "demo", "graph": {"A": ["B"], "B": []}}
    >>> g = Graph(input_graph=json.dumps(data))
    >>> g.vertices()   # ['A', 'B']
    >>> g.edges()      # [Edge('A' -- 'B')]
"""

from __future__ import annotations

import json
import random
import uuid
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from graphworks.edge import Edge
from graphworks.vertex import Vertex

if TYPE_CHECKING:
    from collections.abc import Iterator

    from graphworks.types import AdjacencyMatrix


class Graph:
    """Mutable graph supporting both directed and undirected edges.

    Vertices and edges are stored as first-class objects in a dual-index structure that provides
    O(1) vertex lookup, O(1) edge existence checks, and efficient neighbor iteration.

    The public API preserves backward compatibility: :meth:`vertices` returns a ``list[str]`` of
    names, :meth:`edges` returns ``list[Edge]``, and ``graph[v]`` returns a ``list[str]`` of
    neighbor names.  The richer :class:`~graphworks.vertex.Vertex` and
    :class:`~graphworks.edge.Edge` objects are available via :meth:`get_vertex` and
    :meth:`get_edge`.

    :param label: Human-readable name for this graph.
    :type label: str | None
    :param input_file: Path to a JSON file describing the graph.
    :type input_file: str | None
    :param input_graph: JSON string describing the graph.
    :type input_graph: str | None
    :param input_matrix: Square adjacency matrix (``list[list[int]]``). Non-zero values are
        treated as edges.
    :type input_matrix: AdjacencyMatrix | None
    :raises ValueError: If *input_matrix* is not square, or if edge endpoints in a JSON graph
        reference vertices that do not exist.
    """

    __slots__ = (
        "_label",
        "_is_directed",
        "_is_weighted",
        "_vertices",
        "_adj",
    )

    def __init__(
        self,
        label: str | None = None,
        input_file: str | None = None,
        input_graph: str | None = None,
        input_matrix: AdjacencyMatrix | None = None,
    ) -> None:
        """Initialize a :class:`Graph`.

        Exactly one of *input_file*, *input_graph*, or *input_matrix* should be provided.  If
        none is given an empty graph is created.

        :param label: Human-readable name for this graph.
        :type label: str | None
        :param input_file: Path to a JSON file describing the graph.
        :type input_file: str | None
        :param input_graph: JSON string describing the graph.
        :type input_graph: str | None
        :param input_matrix: Square adjacency matrix (``list[list[int]]``). Non-zero values are
            treated as edges.
        :type input_matrix: AdjacencyMatrix | None
        :raises ValueError: If *input_matrix* is not square, or if edge endpoints in a JSON graph
            reference vertices not in the vertex set.
        """
        self._label: str = label if label is not None else ""
        self._is_directed: bool = False
        self._is_weighted: bool = False
        self._vertices: dict[str, Vertex] = {}
        self._adj: dict[str, dict[str, Edge]] = {}

        if input_file is not None:
            json_data = json.loads(Path(input_file).read_text(encoding="utf-8"))
            self._extract_fields_from_json(json_data)
        elif input_graph is not None:
            json_data = json.loads(input_graph)
            self._extract_fields_from_json(json_data)
        elif input_matrix is not None:
            if not self._validate_matrix(input_matrix):
                msg = "input_matrix is malformed: must be a non-empty square list[list[int]]."
                raise ValueError(msg)
            self._matrix_to_graph(input_matrix)

        if not self._validate():
            msg = (
                "Graph is invalid: edge endpoints reference vertices "
                "that do not exist in the vertex set."
            )
            raise ValueError(msg)

    # ------------------------------------------------------------------
    # Public interface — vertex access
    # ------------------------------------------------------------------

    def vertices(self) -> list[str]:
        """Return all vertex names in insertion order.

        For access to the underlying :class:`~graphworks.vertex.Vertex`
        objects, use :meth:`get_vertex` or :meth:`get_vertices`.

        :return: Vertex name strings.
        :rtype: list[str]
        """
        return list(self._vertices)

    def get_vertex(self, name: str) -> Vertex | None:
        """Return the :class:`~graphworks.vertex.Vertex` with *name*, or ``None``.

        :param name: Vertex name to look up.
        :type name: str
        :return: The vertex object, or ``None`` if not found.
        :rtype: Vertex | None
        """
        return self._vertices.get(name)

    def get_vertices(self) -> list[Vertex]:
        """Return all :class:`~graphworks.vertex.Vertex` objects in insertion order.

        :return: List of vertex objects.
        :rtype: list[Vertex]
        """
        return list(self._vertices.values())

    def add_vertex(self, vertex: str | Vertex) -> None:
        """Add a vertex to the graph if it does not already exist.

        Accepts either a plain name string (which is wrapped in a
        :class:`~graphworks.vertex.Vertex` automatically) or an existing
        :class:`~graphworks.vertex.Vertex` instance.

        :param vertex: Vertex name or :class:`Vertex` object.
        :type vertex: str | Vertex
        :return: Nothing.
        :rtype: None
        """
        if isinstance(vertex, Vertex):
            name = vertex.name
            obj = vertex
        else:
            name = vertex
            obj = Vertex(name)

        if name not in self._vertices:
            self._vertices[name] = obj
            self._adj[name] = {}

    # ------------------------------------------------------------------
    # Public interface — edge access
    # ------------------------------------------------------------------

    def edges(self) -> list[Edge]:
        """Return all edges in the graph.

        For undirected graphs each edge is returned once (the canonical direction is source →
        target in insertion order).

        :return: List of :class:`~graphworks.edge.Edge` objects.
        :rtype: list[Edge]
        """
        return self._collect_edges()

    def get_edge(self, source: str, target: str) -> Edge | None:
        """Return the :class:`~graphworks.edge.Edge` from *source* to *target*, or ``None``.

        For undirected graphs, ``get_edge("A", "B")`` checks both the ``A → B`` and ``B → A``
        slots in the adjacency structure.

        :param source: Source vertex name.
        :type source: str
        :param target: Target vertex name.
        :type target: str
        :return: The edge object, or ``None`` if no such edge exists.
        :rtype: Edge | None
        """
        edge = self._adj.get(source, {}).get(target)
        if edge is not None:
            return edge
        if not self._is_directed:
            return self._adj.get(target, {}).get(source)
        return None

    def add_edge(
        self,
        vertex1: str,
        vertex2: str,
        *,
        weight: float | None = None,
        label: str | None = None,
    ) -> None:
        """Add an edge from *vertex1* to *vertex2*.

        Both vertices are created automatically if they do not yet exist. For undirected graphs,
        the edge is stored once under ``_adj[vertex1][vertex2]``; the reverse lookup is handled
        by :meth:`get_edge` and :meth:`get_neighbors`.

        :param vertex1: Source vertex name.
        :type vertex1: str
        :param vertex2: Destination vertex name.
        :type vertex2: str
        :param weight: Optional numeric weight for the edge.
        :type weight: float | None
        :param label: Optional human-readable label for the edge.
        :type label: str | None
        :return: Nothing.
        :rtype: None
        """
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        edge = Edge(
            source=vertex1,
            target=vertex2,
            directed=self._is_directed,
            weight=weight,
            label=label,
        )
        self._adj[vertex1][vertex2] = edge

    # ------------------------------------------------------------------
    # Public interface — metadata
    # ------------------------------------------------------------------

    def get_label(self) -> str:
        """Return the graph's human-readable label.

        :return: Label string (empty string if not set).
        :rtype: str
        """
        return self._label

    def set_directed(self, is_directed: bool) -> None:
        """Set whether this graph should be treated as directed.

        .. warning::
            Changing directedness on a graph that already contains edges
            does **not** retroactively add or remove reverse edges.  Use
            this only during initial construction.

        :param is_directed: ``True`` for a directed graph, ``False`` for undirected.
        :type is_directed: bool
        :return: Nothing.
        :rtype: None
        """
        self._is_directed = is_directed

    def is_directed(self) -> bool:
        """Return whether this graph is directed.

        :return: ``True`` if directed, ``False`` otherwise.
        :rtype: bool
        """
        return self._is_directed

    def is_weighted(self) -> bool:
        """Return whether this graph was declared as weighted.

        A graph is weighted when its JSON definition includes ``"weighted": true``.  Individual
        edges may carry weights regardless of this flag.

        :return: ``True`` if weighted, ``False`` otherwise.
        :rtype: bool
        """
        return self._is_weighted

    def order(self) -> int:
        """Return the number of vertices in this graph.

        :return: Vertex count (|V|).
        :rtype: int
        """
        return len(self._vertices)

    def size(self) -> int:
        """Return the number of edges in this graph.

        For undirected graphs each edge is counted once.

        :return: Edge count (|E|).
        :rtype: int
        """
        return len(self.edges())

    # ------------------------------------------------------------------
    # Neighbour access
    # ------------------------------------------------------------------

    def get_neighbors(self, v: str) -> list[str]:
        """Return the names of all vertices adjacent to *v*.

        For directed graphs this returns out-neighbors only.  For undirected graphs both ``_adj[
        v]`` targets and vertices that have *v* as a target are included.

        :param v: Vertex name.
        :type v: str
        :return: List of adjacent vertex names.
        :rtype: list[str]
        """
        return self._neighbor_names(v)

    def get_random_vertex(self) -> str:
        """Return a vertex name chosen uniformly at random.

        :return: A random vertex name.
        :rtype: str
        :raises IndexError: If the graph has no vertices.
        """
        return random.choice(self.vertices())

    # ------------------------------------------------------------------
    # Backward-compatible raw access
    # ------------------------------------------------------------------

    def get_graph(self) -> defaultdict[str, list[str]]:
        """Return a ``defaultdict`` adjacency-list view for backward compatibility.

        .. note::
            New code should prefer :meth:`vertices`, :meth:`edges`, :meth:`get_neighbors`,
            or direct ``graph[v]`` access.

        :return: Mapping of vertex names to neighbor-name lists.
        :rtype: defaultdict[str, list[str]]
        """
        result: defaultdict[str, list[str]] = defaultdict(list)
        for name in self._vertices:
            result[name] = self._neighbor_names(name)
        return result

    # ------------------------------------------------------------------
    # Matrix representation (stdlib only — no numpy)
    # ------------------------------------------------------------------

    def get_adjacency_matrix(self) -> AdjacencyMatrix:
        """Compute and return a stdlib adjacency matrix.

        Row and column indices correspond to :meth:`vertices` order. ``matrix[i][j] == 1`` means
        an edge exists from ``vertices()[i]`` to ``vertices()[j]``; ``0`` means no edge.

        The matrix is freshly computed on each call.

        :return: Square adjacency matrix as ``list[list[int]]``.
        :rtype: AdjacencyMatrix
        """
        verts = self.vertices()
        n = len(verts)
        index = {v: i for i, v in enumerate(verts)}
        matrix: AdjacencyMatrix = [[0] * n for _ in range(n)]
        for src, targets in self._adj.items():
            src_idx = index[src]
            for tgt in targets:
                matrix[src_idx][index[tgt]] = 1
        return matrix

    def vertex_to_matrix_index(self, v: str) -> int:
        """Return the row/column index of vertex *v* in the adjacency matrix.

        :param v: Vertex name.
        :type v: str
        :return: Zero-based index into :meth:`vertices`.
        :rtype: int
        :raises ValueError: If *v* is not in the graph.
        """
        return self.vertices().index(v)

    def matrix_index_to_vertex(self, index: int) -> str:
        """Return the vertex name at row/column *index* in the adjacency matrix.

        :param index: Zero-based matrix index.
        :type index: int
        :return: Vertex name.
        :rtype: str
        :raises IndexError: If *index* is out of range.
        """
        return self.vertices()[index]

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return the graph label as its canonical string representation.

        :return: Graph label string.
        :rtype: str
        """
        return self._label

    def __str__(self) -> str:
        """Return a human-readable adjacency-list view of the graph.

        Each line shows ``vertex -> neighbor_names`` (or ``-> 0`` for isolated vertices).  Lines
        are sorted alphabetically by vertex name and preceded by the graph label.

        :return: Multi-line adjacency list string.
        :rtype: str
        """
        lines: list[str] = []
        for name in sorted(self._vertices):
            neighbours = self._neighbor_names(name)
            rhs = "".join(neighbours) if neighbours else "0"
            lines.append(f"{name} -> {rhs}")
        return f"{self._label}\n" + "\n".join(lines)

    def __iter__(self) -> Iterator[str]:
        """Iterate over vertex names in insertion order.

        :return: An iterator yielding vertex name strings.
        :rtype: Iterator[str]
        """
        return iter(self._vertices)

    def __getitem__(self, node: str) -> list[str]:
        """Return neighbour names for *node*, or ``[]`` if absent.

        This enables the common ``graph[v]`` idiom used throughout the algorithm modules.

        :param node: Vertex name.
        :type node: str
        :return: List of neighbour vertex names.
        :rtype: list[str]
        """
        if node not in self._vertices:
            return []
        return self._neighbor_names(node)

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    def _neighbor_names(self, v: str) -> list[str]:
        """Return the neighbour name list for vertex *v*.

        Returns the names of all vertices that *v* has a direct edge to, as recorded in ``_adj[
        v]``.  For undirected graphs, the caller (or the JSON input) is responsible for declaring
        both directions of each edge; this method does **not** synthesize reverse edges.

        :param v: Vertex name.
        :type v: str
        :return: Neighbor name strings.
        :rtype: list[str]
        """
        if v not in self._adj:
            return []
        return list(self._adj[v])

    def _collect_edges(self) -> list[Edge]:
        """Build and return the full edge list from ``_adj``.

        For undirected graphs each pair ``(u, v)`` is returned once, preferring the
        insertion-order direction.

        :return: List of :class:`~graphworks.edge.Edge` instances.
        :rtype: list[Edge]
        """
        edges: list[Edge] = []
        seen: set[tuple[str, str]] = set()
        for src, targets in self._adj.items():
            for tgt, edge in targets.items():
                if self._is_directed:
                    edges.append(edge)
                else:
                    pair = (min(src, tgt), max(src, tgt))
                    if pair not in seen:
                        seen.add(pair)
                        edges.append(edge)
        return edges

    def _extract_fields_from_json(self, json_data: dict) -> None:
        """Populate the graph from a parsed JSON dictionary.

        Reads ``label``, ``directed``, ``weighted``, and ``graph`` keys from *json_data* and
        builds the internal vertex/edge structures.

        Only vertices that appear as **keys** in the ``"graph"`` dict are created.  If an
        adjacency list references a vertex that is not a key, :meth:`_validate` will catch the
        inconsistency after construction.

        :param json_data: Parsed JSON representation of the graph.
        :type json_data: dict
        :return: Nothing.
        :rtype: None
        """
        self._label = json_data.get("label", "")
        self._is_directed = json_data.get("directed", False)
        self._is_weighted = json_data.get("weighted", False)
        raw_graph: dict[str, list[str]] = json_data.get("graph", {})

        # First pass: create all vertices (only keys — not targets).
        for name in raw_graph:
            self.add_vertex(name)

        # Second pass: create edges.  Target vertices that are not keys
        # will be caught by _validate().
        for src, targets in raw_graph.items():
            for tgt in targets:
                edge = Edge(
                    source=src,
                    target=tgt,
                    directed=self._is_directed,
                )
                self._adj[src][tgt] = edge

    def _validate(self) -> bool:
        """Verify that all edge endpoints reference existing vertices.

        :return: ``True`` if the graph is internally consistent.
        :rtype: bool
        """
        for src, targets in self._adj.items():
            if src not in self._vertices:
                return False
            for tgt in targets:
                if tgt not in self._vertices:
                    return False
        return True

    @staticmethod
    def _validate_matrix(matrix: AdjacencyMatrix) -> bool:
        """Return whether *matrix* is a non-empty square 2-D list.

        :param matrix: Candidate adjacency matrix.
        :type matrix: AdjacencyMatrix
        :return: ``True`` if *matrix* is valid.
        :rtype: bool
        """
        if not matrix:
            return False
        n = len(matrix)
        return all(len(row) == n for row in matrix)

    def _matrix_to_graph(self, matrix: AdjacencyMatrix) -> None:
        """Populate the graph from a stdlib adjacency matrix.

        Vertex names are generated as UUID strings to guarantee uniqueness when no external
        naming scheme is available.

        :param matrix: Square adjacency matrix where non-zero values denote edges.
        :type matrix: AdjacencyMatrix
        :return: Nothing.
        :rtype: None
        """
        n = len(matrix)
        names = [str(uuid.uuid4()) for _ in range(n)]

        for name in names:
            self.add_vertex(name)

        for r_idx in range(n):
            for c_idx, val in enumerate(matrix[r_idx]):
                if val > 0:
                    edge = Edge(
                        source=names[r_idx],
                        target=names[c_idx],
                        directed=self._is_directed,
                    )
                    self._adj[names[r_idx]][names[c_idx]] = edge
