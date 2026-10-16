"""Core graph data structure for the graphworks library.

Provides :class:`Graph`, which stores graphs internally using first-class
:class:`~graphworks.vertex.Vertex` and :class:`~graphworks.edge.Edge` objects in a dual-index
adjacency structure:

* ``_vertices``: ``dict[str, Vertex]`` — O(1) lookup by name.
* ``_adj``: ``dict[str, dict[str, Edge]]`` — ``_adj[u][v]`` gives the
:class:`~graphworks.edge.Edge` from *u* to *v* in O(1).

In an undirected graph each edge is stored under **both** endpoints (``_adj[u][v]`` and
``_adj[v][u]`` hold the same :class:`~graphworks.edge.Edge` object), so :meth:`Graph.neighbors`
is symmetric and every algorithm sees ``u`` and ``v`` as adjacent to each other.

Missing vertices
----------------
Lookups that *require* a vertex (``graph[v]``, :meth:`Graph.neighbors`,
:meth:`Graph.vertex_to_index`, and the algorithm functions) raise :class:`KeyError`.  The
``dict.get``-style accessors :meth:`Graph.vertex` and :meth:`Graph.edge` return ``None``.

Construction
------------
A :class:`Graph` can be built from:

* a JSON file path (``input_file``),
* a JSON string (``input_graph``),
* a stdlib adjacency matrix (``input_matrix``), or
* programmatically via :meth:`add_vertex` / :meth:`add_edge`.

Vertices and edges can be deleted with :meth:`remove_vertex` / :meth:`remove_edge`, and
:meth:`copy` returns an independent copy.

Fluent chaining is supported — :meth:`add_vertex`, :meth:`add_edge`, :meth:`add_edges`,
:meth:`remove_vertex`, and :meth:`remove_edge` all return ``self`` so calls can be chained::

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
    >>> g.neighbors("B")  # ['A']
    >>> g.label        # 'demo'
    >>> g.order        # 2
    >>> g.size         # 1

JSON schema
-----------
``"graph"`` maps each vertex name to its neighbors.  A neighbor is either a bare name or an
object carrying edge data; an optional ``"vertices"`` object carries vertex labels and
attributes::

    {
        "label": "roads",
        "directed": false,
        "weighted": true,
        "vertices": {"A": {"label": "Alpha", "attrs": {"x": 1}}},
        "graph": {
            "A": ["B", {"target": "C", "weight": 2.5, "label": "toll", "attrs": {}}],
            "B": [],
            "C": []
        }
    }

In an undirected graph an edge only needs to be listed once (under either endpoint); if it is
listed under both, the first occurrence wins.
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
    :raises ValueError: If more than one input source is given, if *input_matrix* is not square,
        or if a JSON graph has a non-list neighbor value or edge endpoints that reference
        vertices that do not exist.
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

        At most one of *input_file*, *input_graph*, or *input_matrix* may be provided.  If
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
        :raises ValueError: If more than one input source is given, if *input_matrix* is not
            square, or if a JSON graph has a non-list neighbor value or edge endpoints that
            reference vertices not in the vertex set.
        """
        self._label: str = label
        self._directed: bool = directed
        self._weighted: bool = weighted
        self._vertices: dict[str, Vertex] = {}
        self._adj: dict[str, dict[str, Edge]] = {}

        if sum(x is not None for x in (input_file, input_graph, input_matrix)) > 1:
            msg = "Provide at most one of input_file, input_graph, or input_matrix."
            raise ValueError(msg)
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

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        :return: String like ``Graph('my graph', order=5, size=7)``.
        :rtype: str
        """
        return f"Graph({self._label!r}, order={self.order}, size={self.size})"

    def __str__(self) -> str:
        """Return a human-readable adjacency-list view of the graph.

        Each line shows ``vertex -> neighbor, neighbor`` (or ``-> 0`` for isolated vertices).
        Lines are sorted alphabetically by vertex name and preceded by the graph label.

        :return: Multi-line adjacency list string.
        :rtype: str
        """
        lines: list[str] = []
        for name in sorted(self._vertices):
            nbrs = self.neighbors(name)
            rhs = ", ".join(nbrs) if nbrs else "0"
            lines.append(f"{name} -> {rhs}")
        return f"{self._label}\n" + "\n".join(lines)

    def __iter__(self) -> Iterator[str]:
        """Iterate over vertex names in insertion order.

        :return: An iterator yielding vertex name strings.
        :rtype: Iterator[str]
        """
        return iter(self._vertices)

    def __getitem__(self, node: str) -> list[str]:
        """Return neighbor names for *node* (same as :meth:`neighbors`).

        This enables the common ``graph[v]`` idiom used throughout the algorithm modules.

        :param node: Vertex name.
        :type node: str
        :return: List of neighbor vertex names.
        :rtype: list[str]
        :raises KeyError: If *node* is not in the graph.
        """
        return self.neighbors(node)

    def __eq__(self, other: object) -> bool:
        """Return ``True`` if *other* has the same structure.

        Mirrors :class:`Vertex` and :class:`Edge` identity semantics: graphs are equal when they
        agree on :attr:`directed`, the vertex names, and the edge endpoints.  Labels, weights, and
        attributes are descriptive and are not compared.

        :param other: Object to compare against.
        :type other: object
        :return: ``True`` if structurally equal.
        :rtype: bool
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return (
            self._directed == other._directed
            and self._vertices.keys() == other._vertices.keys()
            and all(self._adj[v].keys() == other._adj[v].keys() for v in self._adj)
        )

    __hash__ = None  # type: ignore[assignment]  # mutable, so unhashable

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

    def __or__(self, other: object) -> Graph:
        """Return the union of this graph and *other*.

        Creates a **new** :class:`Graph` containing all vertices and edges from both operands.
        When a vertex name appears in both graphs, the left operand's :class:`Vertex` object is
        kept.  When the same edge ``(source, target)`` exists in both, the right operand's
        :class:`Edge` object wins (last-write-wins, mirroring ``dict.__or__``).

        The operands must agree on :attr:`directed`; mixing directed and undirected graphs raises
        :class:`TypeError`.  The result is :attr:`weighted` if either operand is.

        Example::

            >>> g1 = Graph("left")
            >>> g1.add_edge("A", "B")
            Graph('left', order=2, size=1)
            >>> g2 = Graph("right")
            >>> g2.add_edge("B", "C")
            Graph('right', order=2, size=1)
            >>> merged = g1 | g2
            >>> merged.order
            3
            >>> merged.size
            2

        :param other: Another :class:`Graph` to merge.
        :type other: object
        :return: A new graph containing the union of both operands.
        :rtype: Graph
        :raises TypeError: If *other* is not a :class:`Graph`, or if the graphs disagree on
            :attr:`directed`.
        """
        try:
            other = self._check_union_compat(other)
        except TypeError:
            return NotImplemented

        label = f"{self._label} | {other._label}" if self._label or other._label else ""
        result = Graph(
            label,
            directed=self._directed,
            weighted=self._weighted or other._weighted,
        )

        # Seed with left's vertices (left takes precedence on name collision),
        # then merge right via |=.
        for v_obj in self._vertices.values():
            result.add_vertex(v_obj)
        for targets in self._adj.values():
            for edge in targets.values():
                result.add_edge(edge)

        result |= other
        return result

    def __ior__(self, other: object) -> Self:
        """Merge *other* into this graph in place (augmented union).

        Adds all vertices and edges from *other* to ``self``.  Existing vertices in ``self``
        are kept; new vertices from *other* are added.  Edges from *other* overwrite any
        existing edges with the same ``(source, target)`` pair.

        Returns ``self`` to support chaining and augmented assignment::

            >>> g1 = Graph("base")
            >>> g1.add_edge("A", "B")
            Graph('base', order=2, size=1)
            >>> g2 = Graph()
            >>> g2.add_edge("B", "C")
            Graph('', order=2, size=1)
            >>> g1 |= g2
            >>> g1.order
            3

        :param other: Another :class:`Graph` to merge into ``self``.
        :type other: object
        :return: This graph instance (for chaining).
        :rtype: Self
        :raises TypeError: If *other* is not a :class:`Graph`, or if the graphs disagree on
            :attr:`directed`.
        """
        try:
            other = self._check_union_compat(other)
        except TypeError:
            return NotImplemented

        if other._weighted:
            self._weighted = True

        for v_obj in other._vertices.values():
            self.add_vertex(v_obj)

        for targets in other._adj.values():
            for edge in targets.values():
                self.add_edge(edge)

        return self

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

    def copy(self) -> Graph:
        """Return an independent copy of this graph.

        The copy has the same label, flags, vertices, and edges.  Mutating either graph (adding or
        removing vertices or edges) does not affect the other; the immutable
        :class:`~graphworks.vertex.Vertex` and :class:`~graphworks.edge.Edge` objects are shared.

        :return: A new graph equal to this one.
        :rtype: Graph
        """
        result = Graph(self._label, directed=self._directed, weighted=self._weighted)
        result._vertices = dict(self._vertices)
        result._adj = {v: dict(targets) for v, targets in self._adj.items()}
        return result

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

    def remove_vertex(self, name: str) -> Self:
        """Remove vertex *name* and every edge incident to it.

        Returns ``self`` to support fluent call chaining::

            >>> g = Graph().add_edge("A", "B").add_edge("B", "C")
            >>> g.remove_vertex("B")
            Graph('', order=2, size=0)

        :param name: Vertex name.
        :type name: str
        :return: This graph instance (for chaining).
        :rtype: Self
        :raises KeyError: If *name* is not in the graph.
        """
        for source in self.predecessors(name):
            del self._adj[source][name]
        del self._adj[name]
        del self._vertices[name]
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

        For undirected graphs the argument order does not matter.

        :param source: Source vertex name.
        :type source: str
        :param target: Target vertex name.
        :type target: str
        :return: The edge object, or ``None`` if no such edge exists.
        :rtype: Edge | None
        """
        return self._adj.get(source, {}).get(target)

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
        :raises ValueError: If an :class:`Edge`'s ``directed`` flag differs from the graph's.
        """
        if isinstance(source_or_edge, Edge):
            edge = source_or_edge
            if edge.directed != self._directed:
                kind = "a directed" if self._directed else "an undirected"
                msg = f"Cannot add {edge!r} to {kind} graph: directed flags differ."
                raise ValueError(msg)
        else:
            if target is None:
                msg = "target is required when source_or_edge is a vertex name string."
                raise TypeError(msg)
            edge = Edge(
                source=source_or_edge,
                target=target,
                directed=self._directed,
                weight=weight,
                label=label,
            )

        self.add_vertex(edge.source)
        self.add_vertex(edge.target)
        self._adj[edge.source][edge.target] = edge
        if not self._directed:
            self._adj[edge.target][edge.source] = edge
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

    def remove_edge(self, source: str, target: str) -> Self:
        """Remove the edge from *source* to *target*.

        For undirected graphs the argument order does not matter.  Both vertices are kept.

        Returns ``self`` to support fluent call chaining::

            >>> g = Graph().add_edge("A", "B").add_edge("B", "C")
            >>> g.remove_edge("B", "A")
            Graph('', order=3, size=1)

        :param source: Source vertex name.
        :type source: str
        :param target: Target vertex name.
        :type target: str
        :return: This graph instance (for chaining).
        :rtype: Self
        :raises KeyError: If there is no such edge.
        """
        if self.edge(source, target) is None:
            msg = f"No edge from {source!r} to {target!r} in the graph."
            raise KeyError(msg)
        del self._adj[source][target]
        if not self._directed:
            self._adj[target].pop(source, None)  # absent for a self-loop
        return self

    # ------------------------------------------------------------------
    # Neighbour access
    # ------------------------------------------------------------------

    def neighbors(self, v: str) -> list[str]:
        """Return the names of all vertices adjacent to *v*.

        For directed graphs these are the out-neighbors of *v*.  For undirected graphs adjacency
        is symmetric: if ``B`` is a neighbor of ``A`` then ``A`` is a neighbor of ``B``.

        :param v: Vertex name.
        :type v: str
        :return: List of adjacent vertex names.
        :rtype: list[str]
        :raises KeyError: If *v* is not in the graph.
        """
        if v not in self._adj:
            msg = f"Vertex {v!r} is not in the graph."
            raise KeyError(msg)
        return list(self._adj[v])

    def predecessors(self, v: str) -> list[str]:
        """Return the names of all vertices with an edge *into* *v*.

        For directed graphs these are the in-neighbors of *v*, in vertex insertion order.  For
        undirected graphs this is the same as :meth:`neighbors`.  Runs in O(V).

        :param v: Vertex name.
        :type v: str
        :return: List of vertex names with an edge to *v*.
        :rtype: list[str]
        :raises KeyError: If *v* is not in the graph.
        """
        if not self._directed:
            return self.neighbors(v)
        if v not in self._adj:
            msg = f"Vertex {v!r} is not in the graph."
            raise KeyError(msg)
        return [u for u, targets in self._adj.items() if v in targets]

    # ------------------------------------------------------------------
    # Matrix representation (stdlib only — no numpy)
    # ------------------------------------------------------------------

    def adjacency_matrix(self) -> AdjacencyMatrix:
        """Compute and return a stdlib adjacency matrix.

        Row and column indices correspond to :meth:`vertices` order. ``matrix[i][j] == 1`` means
        an edge exists from ``vertices()[i]`` to ``vertices()[j]``; ``0`` means no edge.  The
        matrix of an undirected graph is symmetric.

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
        :raises KeyError: If *v* is not in the graph.
        """
        if v not in self._vertices:
            msg = f"Vertex {v!r} is not in the graph."
            raise KeyError(msg)
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
    # Protected helpers
    # ------------------------------------------------------------------

    def _collect_edges(self) -> list[Edge]:
        """Build and return the full edge list from ``_adj``.

        Undirected edges are stored under both endpoints but returned once.

        :return: List of :class:`~graphworks.edge.Edge` instances.
        :rtype: list[Edge]
        """
        edges: list[Edge] = []
        seen: set[tuple[str, str]] = set()
        for targets in self._adj.values():
            for edge in targets.values():
                key = (edge.source, edge.target)
                if key not in seen:
                    seen.add(key)
                    edges.append(edge)
        return edges

    def _extract_fields_from_json(self, json_data: dict) -> None:
        """Populate the graph from a parsed JSON dictionary.

        Reads ``label``, ``directed``, ``weighted``, ``vertices``, and ``graph`` keys from
        *json_data* (see the module docstring for the schema).

        :param json_data: Parsed JSON representation of the graph.
        :type json_data: dict
        :return: Nothing.
        :rtype: None
        :raises ValueError: If an adjacency list references a vertex that is not a key of
            ``"graph"``, a neighbor value is not a list, or a neighbor entry is neither a string
            nor an object with ``"target"``.
        """
        self._label = json_data.get("label", "")
        self._directed = json_data.get("directed", False)
        self._weighted = json_data.get("weighted", False)
        raw_graph: dict[str, list[str | dict[str, Any]]] = json_data.get("graph", {})
        raw_vertices: dict[str, dict[str, Any]] = json_data.get("vertices", {})

        for name in raw_graph:
            meta = raw_vertices.get(name, {})
            self.add_vertex(name, label=meta.get("label"), attrs=meta.get("attrs"))

        for src, targets in raw_graph.items():
            if not isinstance(targets, list):
                msg = f"Neighbors of {src!r} must be a list, got {type(targets).__name__}."
                raise ValueError(msg)  # noqa: TRY004 - match sibling JSON errors
            for spec in targets:
                tgt, data = self._parse_neighbor(src, spec)
                if tgt not in self._vertices:
                    msg = f"Edge {src!r} -> {tgt!r} references a vertex not in the graph."
                    raise ValueError(msg)
                if not self._directed and tgt in self._adj and src in self._adj[tgt]:
                    continue  # undirected edge already declared from the other side
                self.add_edge(
                    Edge.create(
                        src,
                        tgt,
                        directed=self._directed,
                        weight=data.get("weight"),
                        label=data.get("label"),
                        attrs=data.get("attrs"),
                    )
                )

    @staticmethod
    def _parse_neighbor(src: str, spec: str | dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Split a JSON neighbor entry into its target name and edge data.

        :param src: Name of the vertex whose adjacency list holds *spec* (for error messages).
        :type src: str
        :param spec: A bare target name, or an object with ``"target"`` and optional edge fields.
        :type spec: str | dict[str, Any]
        :return: The target name and the remaining edge fields.
        :rtype: tuple[str, dict[str, Any]]
        :raises ValueError: If *spec* is neither a string nor an object with ``"target"``.
        """
        match spec:
            case str(tgt):
                return tgt, {}
            case {"target": str(tgt), **data}:
                return tgt, data
            case _:
                msg = f"Invalid neighbor entry for {src!r}: {spec!r}."
                raise ValueError(msg)

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
        names = [str(uuid.uuid4()) for _ in matrix]

        for name in names:
            self.add_vertex(name)

        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val > 0:
                    self.add_edge(names[r_idx], names[c_idx])

    def _check_union_compat(self, other: object) -> Graph:
        """Validate that *other* is a compatible :class:`Graph` for union.

        :param other: Candidate right-hand operand.
        :type other: object
        :return: *other*, narrowed to :class:`Graph`.
        :rtype: Graph
        :raises TypeError: If *other* is not a :class:`Graph` or has a different
            :attr:`directed` flag.
        """
        if not isinstance(other, Graph):
            raise TypeError  # sentinel; callers return NotImplemented instead
        if self._directed != other._directed:
            msg = (
                f"Cannot union a {'directed' if self._directed else 'undirected'} graph "
                f"with a {'directed' if other._directed else 'undirected'} graph."
            )
            raise TypeError(msg)
        return other
