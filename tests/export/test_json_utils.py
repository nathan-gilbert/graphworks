"""Unit tests for :mod:`graphworks.export.json_utils`."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

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
        assert raw["graph"]["a"] == ["b", "c"]
        assert raw["graph"]["b"] == ["a", "c"]

    def test_isolated_vertices_preserved(self, tmp_dir: Path) -> None:
        """Isolated vertices appear in the JSON output with empty lists."""
        data = {"label": "iso", "graph": {"a": [], "b": [], "c": []}}
        original = Graph(input_graph=json.dumps(data))
        save_to_json(original, str(tmp_dir))

        out_path = tmp_dir / "iso.json"
        raw = json.loads(out_path.read_text(encoding="utf-8"))
        assert all(raw["graph"][v] == [] for v in ["a", "b", "c"])
