"""Core graph data structure for the graphworks library.

Provides :class:`Graph`, which stores graphs internally as an adjacency list (``dict[str,
list[str]]``) and exposes a numpy-free adjacency matrix interface via
:data:`~graphworks.types.AdjacencyMatrix`.  Optional numpy interop is available through
:mod:`graphworks.numpy_compat`.
"""

from __future__ import annotations

import json
import random
import uuid
from collections import defaultdict
from typing import TYPE_CHECKING

from graphworks.edge import Edge

if TYPE_CHECKING:
    from collections.abc import Iterator

    from graphworks.types import AdjacencyMatrix


class Graph:
    """Implementation of both undirected and directed graphs.

    Graphs are stored internally as an adjacency-list dictionary (``dict[str, list[str]]``).
    The matrix representation is derived on demand and uses only stdlib types — no numpy required.

    A :class:`Graph` can be constructed from:

    * a JSON file path (``input_file``),
    * a JSON string (``input_graph``), or
    * a stdlib adjacency matrix (``input_matrix``).

    For numpy ``ndarray`` input, convert first with
    :func:`graphworks.numpy_compat.ndarray_to_matrix`.

    Example::

        >>> import json
        >>> from graphworks.graph import Graph
        ...
        >>> data = {"label": "demo", "graph": {"A": ["B"], "B": []}}
        >>> g = Graph(input_graph=json.dumps(data))
        >>> print(g.vertices())   # ['A', 'B']
        >>> print(g.edges())      # [Edge(vertex1='A', vertex2='B', ...)]
    """

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
        :param input_file: Absolute path to a JSON file describing the graph.
        :type input_file: str | None
        :param input_graph: JSON string describing the graph.
        :type input_graph: str | None
        :param input_matrix: Square adjacency matrix (``list[list[int]]``). Non-zero values are
            treated as edges.
        :type input_matrix: AdjacencyMatrix | None
        :raises ValueError: If *input_matrix* is not square, or if edge endpoints in a JSON graph
            reference vertices that do not exist.
        """
        self.__label: str = label if label is not None else ""
        self.__is_directed: bool = False
        self.__is_weighted: bool = False
        self.__graph: defaultdict[str, list[str]] = defaultdict(list)

        if input_file is not None:
            with open(input_file, encoding="utf-8") as in_file:
                json_data = json.loads(in_file.read())
                self.__extract_fields_from_json(json_data)
        elif input_graph is not None:
            json_data = json.loads(input_graph)
            self.__extract_fields_from_json(json_data)
        elif input_matrix is not None:
            if not self.__validate_matrix(input_matrix):
                raise ValueError(
                    "input_matrix is malformed: must be a non-empty square list[list[int]]."
                )
            self.__matrix_to_graph(input_matrix)

        if not self.__validate():
            raise ValueError(
                "Graph is invalid: edge endpoints reference vertices that do not exist in the "
                "vertex set."
            )

    # ------------------------------------------------------------------
    # Public interface — vertices, edges, metadata
    # ------------------------------------------------------------------

    def vertices(self) -> list[str]:
        """Return the list of vertex names in insertion order.

        :return: All vertex names in the graph.
        :rtype: list[str]
        """
        return list(self.__graph.keys())

    def edges(self) -> list[Edge]:
        """Return all edges in the graph.

        For undirected graphs each edge is returned once (the canonical direction is *vertex1 →
        vertex2* in insertion order).

        :return: List of :class:`~graphworks.edge.Edge` objects.
        :rtype: list[Edge]
        """
        return self.__generate_edges()

    def get_graph(self) -> defaultdict[str, list[str]]:
        """Return the raw adjacency-list dictionary.

        :return: The underlying ``defaultdict`` mapping vertex names to their neighbor lists.
        :rtype: DefaultDict[str, list[str]]
        """
        return self.__graph

    def get_label(self) -> str:
        """Return the graph's label.

        :return: Human-readable label string (empty string if not set).
        :rtype: str
        """
        return self.__label

    def set_directed(self, is_directed: bool) -> None:
        """Set whether this graph is directed.

        :param is_directed: ``True`` for a directed graph, ``False`` for undirected.
        :type is_directed: bool
        :return: Nothing
        :rtype: None
        """
        self.__is_directed = is_directed

    def is_directed(self) -> bool:
        """Return whether this graph is directed.

        :return: ``True`` if directed, ``False`` otherwise.
        :rtype: bool
        """
        return self.__is_directed

    def is_weighted(self) -> bool:
        """Return whether this graph has weighted edges.

        :return: ``True`` if weighted, ``False`` otherwise.
        :rtype: bool
        """
        return self.__is_weighted

    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph if it does not already exist.

        :param vertex: Name of the vertex to add.
        :type vertex: str
        :return: Nothing
        :rtype: None
        """
        if vertex not in self.__graph:
            self.__graph[vertex] = []

    def add_edge(self, vertex1: str, vertex2: str) -> None:
        """Add a directed edge from *vertex1* to *vertex2*.

        Both vertices are created automatically if they do not exist.

        :param vertex1: Source vertex name.
        :type vertex1: str
        :param vertex2: Destination vertex name.
        :type vertex2: str
        :return: Nothing
        :rtype: None
        """
        if vertex1 in self.__graph:
            self.__graph[vertex1].append(vertex2)
        else:
            self.__graph[vertex1] = [vertex2]

        if vertex2 not in self.__graph:
            self.__graph[vertex2] = []

    def order(self) -> int:
        """Return the order of the graph (number of vertices).

        :return: Number of vertices.
        :rtype: int
        """
        return len(self.vertices())

    def size(self) -> int:
        """Return the size of the graph (number of edges).

        :return: Number of edges.
        :rtype: int
        """
        return len(self.edges())

    # ------------------------------------------------------------------
    # Matrix representation (stdlib only — no numpy)
    # ------------------------------------------------------------------

    def get_adjacency_matrix(self) -> AdjacencyMatrix:
        """Return a stdlib adjacency matrix for this graph.

        The matrix is always freshly computed from the current adjacency
        list.  Row and column indices correspond to :meth:`vertices` order.

        ``matrix[i][j] == 1`` means an edge exists from ``vertices()[i]``
        to ``vertices()[j]``; ``0`` means no edge.

        :return: Square adjacency matrix as ``list[list[int]]``.
        :rtype: AdjacencyMatrix
        """
        verts = self.vertices()
        n = len(verts)
        index = {v: i for i, v in enumerate(verts)}
        matrix: AdjacencyMatrix = [[0] * n for _ in range(n)]
        for v in verts:
            for neighbour in self.__graph[v]:
                matrix[index[v]][index[neighbour]] = 1
        return matrix

    def vertex_to_matrix_index(self, v: str) -> int:
        """Return the row/column index of vertex *v* in the adjacency matrix.

        :param v: Vertex name.
        :type v: str
        :return: Zero-based index into :meth:`vertices`.
        :rtype: int
        """
        return self.vertices().index(v)

    def matrix_index_to_vertex(self, index: int) -> str:
        """Return the vertex name at row/column *index* in the adjacency matrix.

        :param index: Zero-based matrix index.
        :type index: int
        :return: Vertex name.
        :rtype: str
        """
        return self.vertices()[index]

    # ------------------------------------------------------------------
    # Neighbour access
    # ------------------------------------------------------------------

    def get_neighbors(self, v: str) -> list[str]:
        """Return the neighbours of vertex *v*.

        :param v: Vertex name.
        :type v: str
        :return: List of vertices that *v* has an edge to.
        :rtype: list[str]
        """
        return self.__graph[v]

    def get_random_vertex(self) -> str:
        """Return a uniformly random vertex from the graph.

        :return: A vertex name chosen at random.
        :rtype: str
        """
        return random.choice(self.vertices())

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return the graph label as its canonical representation.

        :return: Graph label string.
        :rtype: str
        """
        return self.__label

    def __str__(self) -> str:
        """Return a human-readable adjacency-list view of the graph.

        :return: Multi-line string with ``vertex -> neighbours`` per line, preceded by the graph
            label.
        :rtype: str
        """
        lines: list[str] = []
        for key in sorted(self.__graph.keys()):
            neighbours = self.__graph[key]
            rhs = "".join(neighbours) if neighbours else "0"
            lines.append(f"{key} -> {rhs}")
        return f"{self.__label}\n" + "\n".join(lines)

    def __iter__(self) -> Iterator[str]:
        """Iterate over vertex names in insertion order.

        :return: An iterator yielding vertex name strings.
        :rtype: Iterator[str]
        """
        return iter(self.vertices())

    def __getitem__(self, node: str) -> list[str]:
        """Return the neighbor list for *node*.

        :param node: Vertex name.
        :type node: str
        :return: List of neighbor vertex names, or an empty list if *node* is not in the graph.
        :rtype: list[str]
        """
        return self.__graph.get(node, [])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def __extract_fields_from_json(self, json_data: dict) -> None:
        """Populate the graph from a parsed JSON dictionary.

        :param json_data: Parsed JSON representation of the graph.
        :type json_data: dict
        :return: Nothing
        :rtype: None
        """
        self.__label = json_data.get("label", "")
        self.__is_directed = json_data.get("directed", False)
        self.__is_weighted = json_data.get("weighted", False)
        raw_graph = json_data.get("graph", {})
        self.__graph: defaultdict[str, list[str]] = defaultdict(
            list,
            raw_graph,
        )

    def __generate_edges(self) -> list[Edge]:
        """Build and return the edge list from the adjacency list.

        For undirected graphs each pair is included only once.

        :return: List of :class:`~graphworks.edge.Edge` instances.
        :rtype: list[Edge]
        """
        edges: list[Edge] = []
        for vertex in self.__graph:
            for neighbour in self.__graph[vertex]:
                if (
                    not self.is_directed()
                    and Edge(neighbour, vertex) not in edges
                    or self.is_directed()
                ):
                    edges.append(Edge(vertex, neighbour))
        return edges

    def __validate(self) -> bool:
        """Verify that all edge endpoints reference existing vertices.

        :return: ``True`` if the graph is internally consistent.
        :rtype: bool
        """
        for vertex in self.__graph:
            for neighbor in self.__graph[vertex]:
                if neighbor not in self.__graph:
                    return False
        return True

    @staticmethod
    def __validate_matrix(matrix: AdjacencyMatrix) -> bool:
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

    def __matrix_to_graph(self, matrix: AdjacencyMatrix) -> None:
        """Populate the adjacency list from a stdlib adjacency matrix.

        Vertex names are generated as UUID strings to guarantee uniqueness.

        :param matrix: Square adjacency matrix where non-zero values denote edges.
        :type matrix: AdjacencyMatrix
        :return: Nothing
        :rtype: None
        """
        n = len(matrix)
        names = [str(uuid.uuid4()) for _ in range(n)]
        for r_idx in range(n):
            vertex = names[r_idx]
            for c_idx, val in enumerate(matrix[r_idx]):
                if val > 0:
                    self.__graph[vertex].append(names[c_idx])
