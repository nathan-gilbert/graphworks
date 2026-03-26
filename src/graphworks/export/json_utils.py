"""JSON export for graphworks graphs.

Provides :func:`save_to_json` for serializing a :class:`~graphworks.graph.Graph` to a JSON file
on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph


def save_to_json(graph: Graph, out_dir: str) -> None:
    """Serialize *graph* to a JSON file in *out_dir*.

    The output file is named ``{graph.label}.json`` and uses the same schema accepted by
    :class:`~graphworks.graph.Graph`'s ``input_file`` constructor parameter::

        {
            "label": "...",
            "directed": false,
            "graph": { "A": ["B"], "B": ["A"] }
        }

    :param graph: The graph to serialize.
    :type graph: Graph
    :param out_dir: Directory path where the JSON file will be written.
    :type out_dir: str
    :return: Nothing.
    :rtype: None
    """
    adjacency: dict[str, list[str]] = {v: graph.neighbors(v) for v in graph.vertices()}

    payload = {
        "label": graph.label,
        "directed": graph.directed,
        "weighted": graph.weighted,
        "graph": adjacency,
    }

    out_path = Path(out_dir) / f"{graph.label}.json"
    out_path.write_text(json.dumps(payload), encoding="utf-8")
