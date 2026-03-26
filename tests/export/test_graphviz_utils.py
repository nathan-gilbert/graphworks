"""Unit tests for :mod:`graphworks.export.graphviz_utils`.

These tests are automatically skipped when the ``graphviz`` Python package
is not installed.  Install with::

    pip install graphworks[viz]
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

graphviz = pytest.importorskip("graphviz", reason="graphviz not installed — skipping DOT tests")

from graphworks.export.graphviz_utils import save_to_dot  # noqa: E402
from graphworks.graph import Graph  # noqa: E402


class TestSaveToDot:
    """Tests for save_to_dot."""

    def test_dot_file_created(self, tmp_dir: Path, simple_edge_graph) -> None:
        """save_to_dot creates a .gv source file."""
        save_to_dot(simple_edge_graph, str(tmp_dir))
        gv_path = tmp_dir / f"{simple_edge_graph.label}.gv"
        assert gv_path.exists()

    def test_undirected_graph_uses_graph_keyword(self, tmp_dir: Path) -> None:
        """An undirected graph produces DOT source with 'graph' keyword."""
        data = {"label": "ug", "graph": {"A": ["B"], "B": ["A"]}}
        graph = Graph(input_graph=json.dumps(data))
        save_to_dot(graph, str(tmp_dir))

        gv_path = tmp_dir / "ug.gv"
        content = gv_path.read_text(encoding="utf-8")
        assert "graph" in content.lower()

    def test_directed_graph_uses_digraph_keyword(self, tmp_dir: Path) -> None:
        """A directed graph produces DOT source with 'digraph' keyword."""
        data = {
            "label": "dg",
            "directed": True,
            "graph": {"A": ["B"], "B": []},
        }
        graph = Graph(input_graph=json.dumps(data))
        save_to_dot(graph, str(tmp_dir))

        gv_path = tmp_dir / "dg.gv"
        content = gv_path.read_text(encoding="utf-8")
        assert "digraph" in content.lower()

    def test_all_vertices_present_in_dot(self, tmp_dir: Path) -> None:
        """All vertex names appear in the DOT source."""
        data = {
            "label": "abc",
            "graph": {"A": ["B"], "B": ["C"], "C": []},
        }
        graph = Graph(input_graph=json.dumps(data))
        save_to_dot(graph, str(tmp_dir))

        gv_path = tmp_dir / "abc.gv"
        content = gv_path.read_text(encoding="utf-8")
        for v in ("A", "B", "C"):
            assert v in content
