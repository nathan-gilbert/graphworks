"""
tests.test_export
~~~~~~~~~~~~~~~~~

Unit and integration tests for :mod:`graphworks.export`.

Covers save_to_json and save_to_dot (Graphviz .gv output).

:author: Nathan Gilbert
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphworks.export.graphviz_utils import save_to_dot
from graphworks.export.json_utils import save_to_json
from graphworks.graph import Graph


class TestSaveToJson:
    """Tests for save_to_json."""

    def test_output_file_is_created(self, simple_edge_graph, tmp_dir: Path) -> None:
        """save_to_json creates a .json file in the output directory."""
        save_to_json(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.json"
        assert out.exists()

    def test_output_content_is_valid_json(self, simple_edge_graph, tmp_dir: Path) -> None:
        """The written file is valid JSON."""
        save_to_json(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.json"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_output_contains_label(self, simple_edge_graph, tmp_dir: Path) -> None:
        """Serialised JSON includes the graph label."""
        save_to_json(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.json"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["label"] == "my graph"

    def test_output_contains_directed_flag(self, simple_edge_graph, tmp_dir: Path) -> None:
        """Serialised JSON includes the directed flag."""
        save_to_json(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.json"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "directed" in data
        assert data["directed"] is False

    def test_output_matches_expected_string(self, simple_edge_graph, tmp_dir: Path) -> None:
        """Serialised output exactly matches expected JSON string."""
        expected = '{"label": "my graph", "directed": false,' ' "graph": {"A": ["B"], "B": []}}'
        save_to_json(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.json"
        assert out.read_text(encoding="utf-8") == expected

    def test_directed_graph_serialised_correctly(self, tmp_dir: Path) -> None:
        """A directed graph serialises with directed=true."""
        data = {"directed": True, "label": "d", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        save_to_json(graph, str(tmp_dir))
        out = tmp_dir / "d.json"
        result = json.loads(out.read_text(encoding="utf-8"))
        assert result["directed"] is True


class TestSaveToDot:
    """Tests for save_to_dot (Graphviz export)."""

    @pytest.fixture(autouse=True)
    def _skip_if_no_graphviz(self) -> None:
        """Skip the test class if the graphviz package is not installed."""
        pytest.importorskip("graphviz")

    def test_dot_file_is_created(self, simple_edge_graph, tmp_dir: Path) -> None:
        """save_to_dot creates a .gv file in the output directory."""

        save_to_dot(simple_edge_graph, str(tmp_dir))
        # graphviz appends .gv to the path we pass
        out = tmp_dir / f"{simple_edge_graph.get_label()}.gv"
        assert out.exists()

    def test_dot_content_matches_expected(self, simple_edge_graph, tmp_dir: Path) -> None:
        """The .gv file contains the expected Graphviz dot language content."""

        expected = "// my graph\ngraph {\n\tA [label=A]\n\tA -- B\n\tB [label=B]\n}\n"
        save_to_dot(simple_edge_graph, str(tmp_dir))
        out = tmp_dir / f"{simple_edge_graph.get_label()}.gv"
        assert out.read_text(encoding="utf-8") == expected

    def test_directed_graph_skipped_by_save_to_dot(self, tmp_dir: Path) -> None:
        """save_to_dot silently skips directed graphs (undirected only)."""

        data = {"directed": True, "label": "d", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(data))
        save_to_dot(graph, str(tmp_dir))
        # no file should be produced for directed graphs
        assert not (tmp_dir / "d.gv").exists()
