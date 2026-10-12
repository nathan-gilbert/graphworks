"""Unit tests for :mod:`graphworks.export.json_utils`."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from graphworks.edge import Edge
from graphworks.export.json_utils import save_to_json
from graphworks.graph import Graph


class TestSaveToJson:
    """Tests for save_to_json."""

    def test_file_created(self, tmp_dir: Path, simple_edge_graph) -> None:
        """save_to_json creates a file named after the graph label."""
        save_to_json(simple_edge_graph, str(tmp_dir))
        out_path = tmp_dir / f"{simple_edge_graph.label}.json"
        assert out_path.exists()

    def test_roundtrip(self, tmp_dir: Path, simple_edge_json) -> None:
        """A graph exported to JSON can be re-imported identically."""
        original = Graph(input_graph=json.dumps(simple_edge_json))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / f"{original.label}.json"
        reloaded = Graph(input_file=str(out_path))

        assert reloaded.label == original.label
        assert reloaded.directed == original.directed
        assert sorted(reloaded.vertices()) == sorted(original.vertices())
        assert reloaded.size == original.size

    def test_directed_flag_preserved(self, tmp_dir: Path) -> None:
        """The directed flag survives a JSON roundtrip."""
        data = {"label": "dag", "directed": True, "graph": {"A": ["B"], "B": []}}
        original = Graph(input_graph=json.dumps(data))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / "dag.json"
        reloaded = Graph(input_file=str(out_path))
        assert reloaded.directed

    def test_weighted_flag_preserved(self, tmp_dir: Path) -> None:
        """The weighted flag survives a JSON roundtrip."""
        data = {"label": "w", "weighted": True, "graph": {"A": [], "B": []}}
        original = Graph(input_graph=json.dumps(data))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / "w.json"
        reloaded = Graph(input_file=str(out_path))
        assert reloaded.weighted

    def test_adjacency_preserved(self, tmp_dir: Path) -> None:
        """Neighbour lists are correctly serialized."""
        data = {
            "label": "tri",
            "graph": {
                "a": ["b", "c"],
                "b": ["a", "c"],
                "c": ["a", "b"],
            },
        }
        original = Graph(input_graph=json.dumps(data))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / "tri.json"
        raw = json.loads(out_path.read_text(encoding="utf-8"))
        # Undirected edges are written once, under their source.
        assert raw["graph"] == {"a": ["b", "c"], "b": ["c"], "c": []}

    def test_isolated_vertices_preserved(self, tmp_dir: Path) -> None:
        """Isolated vertices appear in the JSON output with empty lists."""
        data = {"label": "iso", "graph": {"a": [], "b": [], "c": []}}
        original = Graph(input_graph=json.dumps(data))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / "iso.json"
        raw = json.loads(out_path.read_text(encoding="utf-8"))
        assert all(raw["graph"][v] == [] for v in ["a", "b", "c"])

    def test_returns_written_path(self, tmp_dir: Path, simple_edge_graph) -> None:
        """save_to_json returns the path it wrote."""
        out_path = save_to_json(simple_edge_graph, str(tmp_dir))
        assert out_path == tmp_dir / "my graph.json"
        assert out_path.exists()

    @pytest.mark.parametrize(("label", "name"), [("", "graph.json"), ("a/b", "a_b.json")])
    def test_label_made_filesystem_safe(self, tmp_dir: Path, label: str, name: str) -> None:
        """Empty labels and path separators never escape out_dir."""
        assert save_to_json(Graph(label), str(tmp_dir)) == tmp_dir / name

    def test_edge_and_vertex_data_roundtrip(self, tmp_dir: Path) -> None:
        """Weights, labels, and attributes survive a JSON roundtrip."""
        original = Graph("rich", weighted=True)
        original.add_vertex("A", label="Alpha", attrs={"x": 1})
        original.add_edge(Edge.create("A", "B", weight=2.5, label="toll", attrs={"lanes": 2}))
        original.add_edge("B", "C")

        reloaded = Graph(input_file=str(save_to_json(original, str(tmp_dir))))

        assert reloaded == original
        edge = reloaded.edge("B", "A")
        assert edge is not None
        assert (edge.weight, edge.label, dict(edge.attrs)) == (2.5, "toll", {"lanes": 2})
        vertex = reloaded.vertex("A")
        assert vertex is not None
        assert (vertex.label, dict(vertex.attrs)) == ("Alpha", {"x": 1})

    def test_plain_edges_stay_compact(self, tmp_dir: Path, simple_edge_graph) -> None:
        """Edges without data are written as bare names and no vertices key is emitted."""
        raw = json.loads(save_to_json(simple_edge_graph, str(tmp_dir)).read_text("utf-8"))
        assert raw["graph"] == {"A": ["B"], "B": []}
        assert "vertices" not in raw

    def test_directed_roundtrip(self, tmp_dir: Path, directed_cycle_graph) -> None:
        """Directed graphs round-trip edge-for-edge."""
        directed_cycle_graph.add_edge("C", "A", weight=4)
        path = save_to_json(directed_cycle_graph, str(tmp_dir))
        reloaded = Graph(input_file=str(path))
        assert reloaded == directed_cycle_graph
        assert reloaded.edge("C", "A").weight == 4
