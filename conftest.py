"""
tests.conftest
~~~~~~~~~~~~~~

Shared pytest fixtures for the graphworks test suite.

All fixtures used across multiple test modules live here so pytest discovers
them automatically without explicit imports.

This test suite is written to run against the **installed** package.  In the
typical development workflow::

    uv sync          # installs graphworks in editable mode
    uv run pytest    # runs the suite against the editable install

Alternatively, add the following to ``[tool.pytest.ini_options]`` in
``pyproject.toml`` so that pytest adds ``src/`` to ``sys.path`` for
environments that do not use an editable install::

    pythonpath = ["src"]

Both approaches ensure that ``from src.graphworks.x import Y`` and the
library's internal ``from graphworks.x import Y`` resolve to the **same**
module object, which is required for dataclass ``__eq__`` to work correctly
across the test/library boundary.

:author: Nathan Gilbert
"""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from graphworks.graph import Graph

# ---------------------------------------------------------------------------
# Temporary filesystem helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_dir() -> Generator[Path]:
    """Yield a fresh temporary directory and clean it up afterwards.

    :return: Path to a temporary directory.
    :rtype: Path
    """
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


# ---------------------------------------------------------------------------
# Raw JSON graph definitions (dicts) shared across test modules
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_edge_json() -> dict:
    """Minimal two-vertex undirected graph with one edge (A → B).

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {"label": "my graph", "graph": {"A": ["B"], "B": []}}


@pytest.fixture()
def triangle_json() -> dict:
    """Complete undirected graph on three vertices (K₃).

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "a": ["b", "c"],
            "b": ["a", "c"],
            "c": ["a", "b"],
        }
    }


@pytest.fixture()
def isolated_json() -> dict:
    """Three-vertex graph with no edges (all isolated vertices).

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {"graph": {"a": [], "b": [], "c": []}}


@pytest.fixture()
def connected_json() -> dict:
    """Six-vertex connected undirected graph that includes self-loops.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "a": ["d", "f"],
            "b": ["c", "b"],
            "c": ["b", "c", "d", "e"],
            "d": ["a", "c"],
            "e": ["c"],
            "f": ["a"],
        }
    }


@pytest.fixture()
def big_graph_json() -> dict:
    """Six-vertex connected undirected graph used for diameter tests.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "a": ["c"],
            "b": ["c", "e", "f"],
            "c": ["a", "b", "d", "e"],
            "d": ["c"],
            "e": ["b", "c", "f"],
            "f": ["b", "e"],
        }
    }


@pytest.fixture()
def lollipop_json() -> dict:
    """Lollipop-shaped graph that contains a cycle (d→b) but *no* self-loops.

    ``is_simple`` in this library only checks for self-loops (a vertex listed
    in its own neighbour list), so this graph **is** considered simple despite
    the cycle.  Use :func:`self_loop_json` when you need a graph that is
    definitively not simple.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "z": ["a"],
            "a": ["b"],
            "b": ["c"],
            "c": ["d"],
            "d": ["b"],
        }
    }


@pytest.fixture()
def self_loop_json() -> dict:
    """Two-vertex graph where vertex *a* has a self-loop — **not** simple.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "a": ["a", "b"],
            "b": ["a"],
        }
    }


@pytest.fixture()
def straight_line_json() -> dict:
    """Linear path graph a-b-c-d: simple, no self-loops, no cycles.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {"graph": {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}}


@pytest.fixture()
def directed_dag_json() -> dict:
    """Directed acyclic graph for topological sort and DAG tests.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "directed": True,
        "graph": {
            "A": [],
            "B": [],
            "C": ["D"],
            "D": ["B"],
            "E": ["A", "B"],
            "F": ["A", "C"],
        },
    }


@pytest.fixture()
def directed_cycle_json() -> dict:
    """Directed graph containing a cycle — **not** a DAG.

    The cycle is A → B → D → A (back-edge D→A).

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "directed": True,
        "graph": {
            "A": ["B"],
            "B": ["C", "D"],
            "C": [],
            "D": ["E", "A"],
            "E": [],
        },
    }


@pytest.fixture()
def circuit_json() -> dict:
    """Directed graph with a single Eulerian circuit A → B → C → A.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "directed": True,
        "graph": {"A": ["B"], "B": ["C"], "C": ["A"]},
    }


@pytest.fixture()
def search_graph_json() -> dict:
    """Four-vertex graph used for BFS / DFS traversal tests.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "graph": {
            "a": ["b", "c"],
            "b": ["c"],
            "c": ["a", "d"],
            "d": ["d"],
        }
    }


@pytest.fixture()
def disjoint_directed_json() -> dict:
    """Directed graph with two disjoint components for arrival/departure DFS.

    :return: Graph definition dictionary.
    :rtype: dict
    """
    return {
        "directed": True,
        "graph": {
            "a": ["b", "c"],
            "b": [],
            "c": ["d", "e"],
            "d": ["b", "f"],
            "e": ["f"],
            "f": [],
            "g": ["h"],
            "h": [],
        },
    }


# ---------------------------------------------------------------------------
# Pre-built Graph fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_edge_graph(simple_edge_json) -> Graph:
    """Two-vertex undirected :class:`Graph` with one edge (A → B).

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(simple_edge_json))


@pytest.fixture()
def triangle_graph(triangle_json) -> Graph:
    """Complete undirected :class:`Graph` on three vertices (K₃).

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(triangle_json))


@pytest.fixture()
def isolated_graph(isolated_json) -> Graph:
    """Three-vertex :class:`Graph` with no edges.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(isolated_json))


@pytest.fixture()
def connected_graph(connected_json) -> Graph:
    """Six-vertex connected undirected :class:`Graph`.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(connected_json))


@pytest.fixture()
def big_graph(big_graph_json) -> Graph:
    """Six-vertex connected undirected :class:`Graph` for diameter tests.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(big_graph_json))


@pytest.fixture()
def directed_dag(directed_dag_json) -> Graph:
    """Directed acyclic :class:`Graph`.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(directed_dag_json))


@pytest.fixture()
def directed_cycle_graph(directed_cycle_json) -> Graph:
    """Directed :class:`Graph` containing a cycle.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(directed_cycle_json))


@pytest.fixture()
def circuit_graph(circuit_json) -> Graph:
    """Directed :class:`Graph` with an Eulerian circuit A → B → C → A.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(circuit_json))


@pytest.fixture()
def search_graph(search_graph_json) -> Graph:
    """Four-vertex :class:`Graph` for BFS / DFS tests.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(search_graph_json))


@pytest.fixture()
def disjoint_directed_graph(disjoint_directed_json) -> Graph:
    """Directed :class:`Graph` with two disjoint components.

    :return: Constructed Graph instance.
    :rtype: Graph
    """
    return Graph(input_graph=json.dumps(disjoint_directed_json))
