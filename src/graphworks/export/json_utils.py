"""JSON export for graphworks graphs.

Provides :func:`save_to_json` for serializing a :class:`~graphworks.graph.Graph` to a JSON file
on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..utilities import _file_stem

if TYPE_CHECKING:
    from ..graph import Graph


def save_to_json(graph: Graph, out_dir: str) -> Path:
    """Serialize *graph* to a JSON file in *out_dir*.

    The output file is named after :attr:`~graphworks.graph.Graph.label` (path separators
    replaced with ``_``; ``graph.json`` if unlabeled) and uses the schema accepted by
    :class:`~graphworks.graph.Graph`'s ``input_file`` parameter.  Vertex labels and attributes and
    edge weights, labels, and attributes are preserved, so the file round-trips losslessly::

        {
            "label": "...",
            "directed": false,
            "weighted": true,
            "vertices": {"A": {"label": "Alpha"}},
            "graph": {"A": [{"target": "B", "weight": 2}], "B": []}
        }

    Undirected edges are written once, under their source vertex.  ``"vertices"`` is omitted
    when no vertex has a label or attributes.

    :param graph: The graph to serialize.
    :type graph: Graph
    :param out_dir: Directory path where the JSON file will be written.
    :type out_dir: str
    :return: Path of the written file.
    :rtype: Path
    """
    adjacency: dict[str, list[str | dict[str, Any]]] = {v: [] for v in graph}
    for edge in graph.edges():
        data = _present(weight=edge.weight, label=edge.label, attrs=dict(edge.attrs))
        adjacency[edge.source].append({"target": edge.target, **data} if data else edge.target)

    vertices: dict[str, dict[str, Any]] = {}
    for name in graph:
        vertex = graph.vertex(name)
        meta = _present(label=vertex.label, attrs=dict(vertex.attrs)) if vertex else {}
        if meta:
            vertices[name] = meta

    payload: dict[str, Any] = {
        "label": graph.label,
        "directed": graph.directed,
        "weighted": graph.weighted,
    }
    if vertices:
        payload["vertices"] = vertices
    payload["graph"] = adjacency

    out_path = Path(out_dir) / f"{_file_stem(graph.label)}.json"
    out_path.write_text(json.dumps(payload), encoding="utf-8")
    return out_path


def _present(**fields: Any) -> dict[str, Any]:
    """Return *fields* without the ones that are ``None`` or empty dicts.

    :param fields: Candidate JSON fields.
    :type fields: Any
    :return: Only the fields worth writing.
    :rtype: dict[str, Any]
    """
    return {k: v for k, v in fields.items() if v is not None and v != {}}
