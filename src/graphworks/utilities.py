"""Module containing utility functions for graphworks."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any


def _freeze_attrs(raw: dict[str, Any] | None) -> MappingProxyType[str, Any]:
    """Return a read-only *copy* of *raw*, defaulting to an empty mapping.

    The input dict is copied so that later mutations to the caller's original dict do not
    propagate into the frozen vertex.

    :param raw: Mutable attribute dictionary (or ``None``).
    :type raw: dict[str, Any] | None
    :return: Immutable mapping proxy.
    :rtype: MappingProxyType[str, Any]
    """
    return MappingProxyType(dict(raw) if raw is not None else {})
