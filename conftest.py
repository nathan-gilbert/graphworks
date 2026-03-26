"""Shared pytest fixtures for the graphworks test suite.

All fixtures used across multiple test modules live here so pytest discovers them automatically
without explicit imports.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest

from graphworks.graph import Graph

# ---------------------------------------------------------------------------
# Temporary filesystem helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_dir() -> Generator[Path]:
    """Yield a fresh temporary directory and clean it up afterwards."""
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


# ---------------------------------------------------------------------------
# Raw JSON graph definitions
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_edge_json() -> dict:
    """Minimal two-vertex undirected graph with one edge (A → B)."""
    return {"label": "my graph", "graph": {"A": ["B"], "B": []}}


@pytest.fixture
def triangle_json() -> dict:
    """Complete undirected graph on three vertices (K₃)."""
    return {
        "graph": {
            "a": ["b", "c"],
            "b": ["a", "c"],
            "c": ["a", "b"],
        }
    }


@pytest.fixture
def isolated_json() -> dict:
    """Three-vertex graph with no edges."""
    return {"graph": {"a": [], "b": [], "c": []}}


@pytest.fixture
def connected_json() -> dict:
    """Six-vertex connected undirected graph with self-loops."""
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


@pytest.fixture
def big_graph_json() -> dict:
    """Six-vertex connected undirected graph used for diameter tests."""
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


@pytest.fixture
def lollipop_json() -> dict:
    """Lollipop-shaped graph with a cycle but no self-loops."""
    return {
        "graph": {
            "z": ["a"],
            "a": ["b"],
            "b": ["c"],
            "c": ["d"],
            "d": ["b"],
        }
    }


@pytest.fixture
def self_loop_json() -> dict:
    """Two-vertex graph where vertex *a* has a self-loop."""
    return {"graph": {"a": ["a", "b"], "b": ["a"]}}


@pytest.fixture
def straight_line_json() -> dict:
    """Linear path graph a-b-c-d."""
    return {"graph": {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}}


@pytest.fixture
def directed_dag_json() -> dict:
    """Directed acyclic graph for topological sort and DAG tests."""
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


@pytest.fixture
def directed_cycle_json() -> dict:
    """Directed graph containing a cycle (A → B → D → A)."""
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


@pytest.fixture
def circuit_json() -> dict:
    """Directed graph with a single Eulerian circuit A → B → C → A."""
    return {
        "directed": True,
        "graph": {"A": ["B"], "B": ["C"], "C": ["A"]},
    }


@pytest.fixture
def search_graph_json() -> dict:
    """Four-vertex graph used for BFS / DFS traversal tests."""
    return {
        "graph": {
            "a": ["b", "c"],
            "b": ["c"],
            "c": ["a", "d"],
            "d": ["d"],
        }
    }


@pytest.fixture
def disjoint_directed_json() -> dict:
    """Directed graph with two disjoint components."""
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


@pytest.fixture
def simple_edge_graph(simple_edge_json: dict) -> Graph:
    """Two-vertex undirected Graph with one edge (A → B)."""
    return Graph(input_graph=json.dumps(simple_edge_json))


@pytest.fixture
def triangle_graph(triangle_json: dict) -> Graph:
    """Complete undirected Graph on three vertices (K₃)."""
    return Graph(input_graph=json.dumps(triangle_json))


@pytest.fixture
def isolated_graph(isolated_json: dict) -> Graph:
    """Three-vertex Graph with no edges."""
    return Graph(input_graph=json.dumps(isolated_json))


@pytest.fixture
def connected_graph(connected_json: dict) -> Graph:
    """Six-vertex connected undirected Graph."""
    return Graph(input_graph=json.dumps(connected_json))


@pytest.fixture
def big_graph(big_graph_json: dict) -> Graph:
    """Six-vertex connected undirected Graph for diameter tests."""
    return Graph(input_graph=json.dumps(big_graph_json))


@pytest.fixture
def directed_dag(directed_dag_json: dict) -> Graph:
    """Directed acyclic Graph."""
    return Graph(input_graph=json.dumps(directed_dag_json))


@pytest.fixture
def directed_cycle_graph(directed_cycle_json: dict) -> Graph:
    """Directed Graph containing a cycle."""
    return Graph(input_graph=json.dumps(directed_cycle_json))


@pytest.fixture
def circuit_graph(circuit_json: dict) -> Graph:
    """Directed Graph with an Eulerian circuit."""
    return Graph(input_graph=json.dumps(circuit_json))


@pytest.fixture
def search_graph(search_graph_json: dict) -> Graph:
    """Four-vertex Graph for BFS / DFS tests."""
    return Graph(input_graph=json.dumps(search_graph_json))


@pytest.fixture
def disjoint_directed_graph(disjoint_directed_json: dict) -> Graph:
    """Directed Graph with two disjoint components."""
    return Graph(input_graph=json.dumps(disjoint_directed_json))
