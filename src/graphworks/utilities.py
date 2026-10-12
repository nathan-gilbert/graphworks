"""Module containing utility functions for graphworks."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any


def _freeze_attrs(raw: dict[str, Any] | None) -> MappingProxyType[str, Any]:
    """Return a read-only *copy* of *raw*, defaulting to an empty mapping.

    The input dict is copied so that later mutations to the caller's original dict do not
    propagate into the frozen vertex or edge.

    :param raw: Mutable attribute dictionary (or ``None``).
    :type raw: dict[str, Any] | None
    :return: Immutable mapping proxy.
    :rtype: MappingProxyType[str, Any]
    """
    return MappingProxyType(dict(raw) if raw is not None else {})


def _file_stem(label: str) -> str:
    """Return a filesystem-safe file stem for a graph *label*.

    Path separators are replaced with ``_`` and an empty label becomes ``"graph"`` (matching the
    renderers' fallback), so exporters never write outside their target directory.

    :param label: Graph label.
    :type label: str
    :return: A non-empty file stem.
    :rtype: str
    """
    return label.replace("/", "_").replace("\\", "_") or "graph"
