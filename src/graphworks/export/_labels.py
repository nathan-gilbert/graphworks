"""Shared label and weight formatting for the graph renderers.

Both :mod:`graphworks.export.text_utils` and :mod:`graphworks.export.ascii_utils` resolve what
text to show for a vertex and what annotation to show for an edge through the helpers here, so the
two styles can never drift.  :class:`RenderStyle` bundles the three display toggles common to
``to_text`` and ``to_ascii``.

The toggles default to "show when present", which is backward-compatible: a graph with no custom
vertex/edge labels and ``weighted=False`` renders exactly as it did before these options existed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph


@dataclass(frozen=True, slots=True)
class RenderStyle:
    """Display toggles shared by the text and ASCII renderers.

    :param vertex_labels: Show a vertex's :attr:`~graphworks.vertex.Vertex.label` when set,
        falling back to its name.
    :type vertex_labels: bool
    :param edge_labels: Show an edge's :attr:`~graphworks.edge.Edge.label` when set.
    :type edge_labels: bool
    :param weights: Show edge weights.  ``None`` (the default) follows the graph's
        :attr:`~graphworks.graph.Graph.weighted` flag; ``True``/``False`` force the choice.
    :type weights: bool | None
    """

    vertex_labels: bool = True
    edge_labels: bool = True
    weights: bool | None = None


def vertex_text(graph: Graph, name: str, *, use_label: bool = True) -> str:
    """Return the display text for vertex *name*.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param name: The vertex name (its identity key).
    :type name: str
    :param use_label: When ``True``, prefer the vertex's label if one is set.
    :type use_label: bool
    :return: The vertex label if requested and present, otherwise the name.
    :rtype: str
    """
    vertex = graph.vertex(name)
    if use_label and vertex is not None and vertex.label:
        return vertex.label
    return name


def edge_annotation(
    graph: Graph,
    source: str | None,
    target: str,
    *,
    style: RenderStyle,
) -> str:
    """Return the bare annotation for the *source* → *target* edge (no surrounding punctuation).

    Combines the edge label and/or weight into a comma-separated string such as ``"retry, w=3"``.
    Returns ``""`` when there is no edge, no source, or nothing to show.  Callers wrap the result
    as they see fit — ``to_text`` brackets it, ``to_ascii`` stamps it at the edge midpoint.

    :param graph: The graph being rendered.
    :type graph: Graph
    :param source: The edge's source vertex, or ``None`` for a root (no incoming edge).
    :type source: str | None
    :param target: The edge's target vertex.
    :type target: str
    :param style: The active display toggles.
    :type style: RenderStyle
    :return: The annotation content, or ``""``.
    :rtype: str
    """
    if source is None:
        return ""
    edge = graph.edge(source, target)
    if edge is None:
        return ""

    parts: list[str] = []
    if style.edge_labels and edge.label:
        parts.append(edge.label)
    show_weights = graph.weighted if style.weights is None else style.weights
    if show_weights and edge.weight is not None:
        parts.append(f"w={edge.weight}")
    return ", ".join(parts)
