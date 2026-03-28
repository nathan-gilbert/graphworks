"""Core graph data structure for the graphworks library.

Provides :class:`Graph`, which stores graphs internally using first-class
:class:`~graphworks.vertex.Vertex` and :class:`~graphworks.edge.Edge` objects in a dual-index
adjacency structure:

* ``_vertices``: ``dict[str, Vertex]`` — O(1) lookup by name.
* ``_adj``: ``dict[str, dict[str, Edge]]`` — ``_adj[u][v]`` gives the
:class:`~graphworks.edge.Edge` from *u* to *v* in O(1).

Construction
------------
A :class:`Graph` can be built from:

* a JSON file path (``input_file``),
* a JSON string (``input_graph``),
* a stdlib adjacency matrix (``input_matrix``), or
* programmatically via :meth:`add_vertex` / :meth:`add_edge`.

Fluent chaining is supported — :meth:`add_vertex`, :meth:`add_edge`, and :meth:`add_edges` all
return ``self`` so calls can be chained::

    >>> g = Graph("demo")
    >>> g.add_edge("A", "B").add_edge("B", "C").add_edge("C", "A")
    Graph('demo', order=3, size=3)

For numpy ``ndarray`` input, convert first with :func:`graphworks.numpy_compat.ndarray_to_matrix`.

Example::

    >>> import json
    >>> from graphworks.graph import Graph  # noqa
    ...
    >>> data = {"label": "demo", "graph": {"A": ["B"], "B": []}}
    >>> g = Graph(input_graph=json.dumps(data))
    >>> g.vertices()   # ['A', 'B']
    >>> g.edges()      # [Edge('A' -- 'B')]
    >>> g.label        # 'demo'
    >>> g.order        # 2
    >>> g.size         # 1
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from .edge import Edge
from .vertex import Vertex

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Any, Self

    from .types import AdjacencyMatrix


class Graph:
    """Mutable graph supporting both directed and undirected edges.

    Vertices and edges are stored as first-class objects in a dual-index structure that provides
    O(1) vertex lookup, O(1) edge existence checks, and efficient neighbor iteration.

    :param label: Human-readable name for this graph.
    :type label: str
    :param input_file: Path to a JSON file describing the graph.
    :type input_file: str | None
    :param input_graph: JSON string describing the graph.
    :type input_graph: str | None
    :param input_matrix: Square adjacency matrix (``list[list[int]]``). Non-zero values are
        treated as edges.
    :type input_matrix: AdjacencyMatrix | None
    :param directed: Whether this graph is directed.  Defaults to ``False``. Can be overridden by
        the ``"directed"`` key in JSON input.
    :type directed: bool
    :param weighted: Whether this graph uses weighted edges.  Defaults to ``False``.  Can be
        overridden by the ``"weighted"`` key in JSON input.
    :type weighted: bool
    :raises ValueError: If *input_matrix* is not square, or if edge endpoints in a JSON graph
        reference vertices that do not exist.
    """

    __slots__ = (
        "_label",
        "_directed",
        "_weighted",
        "_vertices",
        "_adj",
    )

    def __init__(  # noqa: PLR0913
        self,
        label: str = "",
        *,
        input_file: str | None = None,
        input_graph: str | None = None,
        input_matrix: AdjacencyMatrix | None = None,
        directed: bool = False,
        weighted: bool = False,
    ) -> None:
        """Initialize a :class:`Graph`.

        At most one of *input_file*, *input_graph*, or *input_matrix* should be provided.  If
        none is given an empty graph is created.

        :param label: Human-readable name for this graph.
        :type label: str
        :param input_file: Path to a JSON file describing the graph.
        :type input_file: str | None
        :param input_graph: JSON string describing the graph.
        :type input_graph: str | None
        :param input_matrix: Square adjacency matrix (``list[list[int]]``). Non-zero values are
            treated as edges.
        :type input_matrix: AdjacencyMatrix | None
        :param directed: Whether this graph is directed.
        :type directed: bool
        :param weighted: Whether this graph uses weighted edges.
        :type weighted: bool
        :raises ValueError: If *input_matrix* is not square, or if edge endpoints in a JSON graph
            reference vertices not in the vertex set.
        """
        self._label: str = label
        self._directed: bool = directed
        self._weighted: bool = weighted
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
                msg = "input_matrix is malformed: must be a non-empty " "square list[list[int]]."
                raise ValueError(msg)
            self._matrix_to_graph(input_matrix)

        if not self._validate():
            msg = (
                "Graph is invalid: edge endpoints reference vertices that do not exist in the "
                "vertex set."
            )
            raise ValueError(msg)

    # ------------------------------------------------------------------
    # Properties — metadata
    # ------------------------------------------------------------------

    @property
    def label(self) -> str:
        """Human-readable name for this graph.

        :return: Label string (empty string if not set).
        :rtype: str
        """
        return self._label

    @property
    def directed(self) -> bool:
        """Whether this graph is directed.

        :return: ``True`` if directed, ``False`` otherwise.
        :rtype: bool
        """
        return self._directed

    @property
    def weighted(self) -> bool:
        """Whether this graph was declared as weighted.

        :return: ``True`` if weighted, ``False`` otherwise.
        :rtype: bool
        """
        return self._weighted

    @property
    def order(self) -> int:
        """Number of vertices in this graph (|V|).

        :return: Vertex count.
        :rtype: int
        """
        return len(self._vertices)

    @property
    def size(self) -> int:
        """Number of edges in this graph (|E|).

        For undirected graphs each edge is counted once.

        :return: Edge count.
        :rtype: int
        """
        return len(self.edges())

    # ------------------------------------------------------------------
    # Vertex access
    # ------------------------------------------------------------------

    def vertices(self) -> list[str]:
        """Return all vertex names in insertion order.

        :return: Vertex name strings.
        :rtype: list[str]
        """
        return list(self._vertices)

    def vertex(self, name: str) -> Vertex | None:
        """Return the :class:`~graphworks.vertex.Vertex` with *name*, or ``None``.

        :param name: Vertex name to look up.
        :type name: str
        :return: The vertex object, or ``None`` if not found.
        :rtype: Vertex | None
        """
        return self._vertices.get(name)

    def add_vertex(
        self,
        vertex: str | Vertex,
        *,
        label: str | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> Self:
        """Add a vertex to the graph if it does not already exist.

        Accepts a plain name string, a :class:`~graphworks.vertex.Vertex` instance, or a name
        string with keyword arguments that are forwarded to :meth:`Vertex.create`.

        When *vertex* is a :class:`Vertex` object, *label* and *attrs* are ignored — the object
        is used as-is.

        Returns ``self`` to support fluent call chaining::

            >>> g = Graph()
            >>> g.add_vertex("A").add_vertex("B").add_vertex("C")
            Graph('', order=3, size=0)

        :param vertex: Vertex name or :class:`Vertex` object.
        :type vertex: str | Vertex
        :param label: Human-readable display label.  Only used when *vertex* is a ``str``.
        :type label: str | None
        :param attrs: Arbitrary metadata dict.  Only used when *vertex* is a ``str``.  The dict is
            defensively copied and frozen into a :class:`~types.MappingProxyType`.
        :type attrs: dict[str, Any] | None
        :return: This graph instance (for chaining).
        :rtype: Self
        """
        if isinstance(vertex, Vertex):
            name = vertex.name
            obj = vertex
        elif label is not None or attrs is not None:
            name = vertex
            obj = Vertex.create(name, label=label, attrs=attrs)
        else:
            name = vertex
            obj = Vertex(name)

        if name not in self._vertices:
            self._vertices[name] = obj
            self._adj[name] = {}

        return self

    # ------------------------------------------------------------------
    # Edge access
    # ------------------------------------------------------------------

    def edges(self) -> list[Edge]:
        """Return all edges in the graph.

        For undirected graphs each edge is returned once (the canonical direction is source →
        target in insertion order).

        :return: List of :class:`~graphworks.edge.Edge` objects.
        :rtype: list[Edge]
        """
        return self._collect_edges()

    def edge(self, source: str, target: str) -> Edge | None:
        """Return the :class:`~graphworks.edge.Edge` from *source* to *target*.

        For undirected graphs, checks both the ``source → target`` and ``target → source`` slots
        in the adjacency structure.

        :param source: Source vertex name.
        :type source: str
        :param target: Target vertex name.
        :type target: str
        :return: The edge object, or ``None`` if no such edge exists.
        :rtype: Edge | None
        """
        found = self._adj.get(source, {}).get(target)
        if found is not None:
            return found
        if not self._directed:
            return self._adj.get(target, {}).get(source)
        return None

    def add_edge(
        self,
        source_or_edge: str | Edge,
        target: str | None = None,
        *,
        weight: float | None = None,
        label: str | None = None,
    ) -> Self:
        """Add an edge to the graph.

        Accepts either two vertex-name strings **or** a pre-built :class:`~graphworks.edge.Edge`
        object.  Both endpoint vertices are created automatically if they do not yet exist.

        When an :class:`Edge` object is passed, *target*, *weight*, and *label* are ignored — the
        edge is used as-is.

        Returns ``self`` to support fluent call chaining::

            >>> g = Graph("triangle")
            >>> g.add_edge("A", "B").add_edge("B", "C").add_edge("C", "A")
            Graph('triangle', order=3, size=3)

        :param source_or_edge: Source vertex name **or** an :class:`Edge` instance.
        :type source_or_edge: str | Edge
        :param target: Destination vertex name.  Required when *source_or_edge* is a ``str``;
            ignored when it is an :class:`Edge`.
        :type target: str | None
        :param weight: Optional numeric weight for the edge.  Ignored when *source_or_edge* is an
            :class:`Edge`.
        :type weight: float | None
        :param label: Optional human-readable label for the edge.  Ignored when *source_or_edge*
            is an :class:`Edge`.
        :type label: str | None
        :return: This graph instance (for chaining).
        :rtype: Self
        :raises TypeError: If *source_or_edge* is a ``str`` and *target* is ``None``.
        """
        if isinstance(source_or_edge, Edge):
            edge = source_or_edge
            self.add_vertex(edge.source)
            self.add_vertex(edge.target)
            self._adj[edge.source][edge.target] = edge
        else:
            if target is None:
                msg = "target is required when source_or_edge is a vertex name string."
                raise TypeError(msg)
            self.add_vertex(source_or_edge)
            self.add_vertex(target)
            edge = Edge(
                source=source_or_edge,
                target=target,
                directed=self._directed,
                weight=weight,
                label=label,
            )
            self._adj[source_or_edge][target] = edge

        return self

    def add_edges(
        self,
        edges: Iterable[tuple[str, str] | tuple[str, str, dict[str, Any]] | Edge],
    ) -> Self:
        """Add multiple edges to the graph in one call.

        Each element of *edges* can be:

        * a ``(source, target)`` tuple,
        * a ``(source, target, attrs_dict)`` tuple where *attrs_dict* may contain ``"weight"``
          and/or ``"label"`` keys, or
        * a pre-built :class:`~graphworks.edge.Edge` object.

        Returns ``self`` to support fluent call chaining::

            >>> g = Graph("square")
            >>> g.add_edges([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])
            Graph('square', order=4, size=4)

        :param edges: Iterable of edge specifications.
        :type edges: Iterable[tuple[str, str] | tuple[str, str, dict[str, Any]] | Edge]
        :return: This graph instance (for chaining).
        :rtype: Self
        :raises TypeError: If an element is not a recognized edge specification.
        """
        for item in edges:
            match item:
                case Edge() as edge:
                    self.add_edge(edge)
                case (str(src), str(tgt)):
                    self.add_edge(src, tgt)
                case (str(src), str(tgt), dict(kwargs)):
                    self.add_edge(
                        src,
                        tgt,
                        weight=kwargs.get("weight"),
                        label=kwargs.get("label"),
                    )
                case (str(), str(), invalid):
                    msg = (
                        f"Third element of edge tuple must be a dict, "
                        f"got {type(invalid).__name__}."
                    )
                    raise TypeError(msg)
                case tuple():
                    msg = f"Edge tuple must have 2 or 3 str elements, got {len(item)}."
                    raise TypeError(msg)
                case _:
                    msg = f"Expected a tuple or Edge, got {type(item).__name__}."
                    raise TypeError(msg)

        return self

    # ------------------------------------------------------------------
    # Neighbour access
    # ------------------------------------------------------------------

    def neighbors(self, v: str) -> list[str]:
        """Return the names of all vertices adjacent to *v*.

        Returns the out-neighbors of *v* as recorded in the adjacency structure.  For undirected
        graphs, the JSON input (or programmatic :meth:`add_edge` calls) is expected to declare
        both directions.

        :param v: Vertex name.
        :type v: str
        :return: List of adjacent vertex names.
        :rtype: list[str]
        """
        if v not in self._adj:
            return []
        return list(self._adj[v])

    # ------------------------------------------------------------------
    # Matrix representation (stdlib only — no numpy)
    # ------------------------------------------------------------------

    def adjacency_matrix(self) -> AdjacencyMatrix:
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

    def vertex_to_index(self, v: str) -> int:
        """Return the row/column index of vertex *v* in the adjacency matrix.

        :param v: Vertex name.
        :type v: str
        :return: Zero-based index into :meth:`vertices`.
        :rtype: int
        :raises ValueError: If *v* is not in the graph.
        """
        return self.vertices().index(v)

    def index_to_vertex(self, index: int) -> str:
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
        """Return a developer-friendly representation.

        :return: String like ``Graph('my graph', order=5, size=7)``.
        :rtype: str
        """
        return f"Graph({self._label!r}, order={self.order}, size={self.size})"

    def __str__(self) -> str:
        """Return a human-readable adjacency-list view of the graph.

        Each line shows ``vertex -> neighbor_names`` (or ``-> 0`` for isolated vertices).  Lines
        are sorted alphabetically by vertex name and preceded by the graph label.

        :return: Multi-line adjacency list string.
        :rtype: str
        """
        lines: list[str] = []
        for name in sorted(self._vertices):
            nbrs = self.neighbors(name)
            rhs = "".join(nbrs) if nbrs else "0"
            lines.append(f"{name} -> {rhs}")
        return f"{self._label}\n" + "\n".join(lines)

    def __iter__(self) -> Iterator[str]:
        """Iterate over vertex names in insertion order.

        :return: An iterator yielding vertex name strings.
        :rtype: Iterator[str]
        """
        return iter(self._vertices)

    def __getitem__(self, node: str) -> list[str]:
        """Return neighbor names for *node*, or ``[]`` if absent.

        This enables the common ``graph[v]`` idiom used throughout the algorithm modules.

        :param node: Vertex name.
        :type node: str
        :return: List of neighbor vertex names.
        :rtype: list[str]
        """
        if node not in self._vertices:
            return []
        return self.neighbors(node)

    def __contains__(self, item: str) -> bool:
        """Return ``True`` if *item* is a vertex name in this graph.

        :param item: Vertex name to check.
        :type item: str
        :return: ``True`` if the vertex exists.
        :rtype: bool
        """
        return item in self._vertices

    def __len__(self) -> int:
        """Return the number of vertices (same as :attr:`order`).

        :return: Vertex count.
        :rtype: int
        """
        return len(self._vertices)

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

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
                if self._directed:
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
        inconsistency.

        :param json_data: Parsed JSON representation of the graph.
        :type json_data: dict
        :return: Nothing.
        :rtype: None
        """
        self._label = json_data.get("label", "")
        self._directed = json_data.get("directed", False)
        self._weighted = json_data.get("weighted", False)
        raw_graph: dict[str, list[str]] = json_data.get("graph", {})

        for name in raw_graph:
            self.add_vertex(name)

        for src, targets in raw_graph.items():
            for tgt in targets:
                edge = Edge(
                    source=src,
                    target=tgt,
                    directed=self._directed,
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

        Vertex names are generated as UUID strings to guarantee uniqueness.

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
                        directed=self._directed,
                    )
                    self._adj[names[r_idx]][names[c_idx]] = edge
