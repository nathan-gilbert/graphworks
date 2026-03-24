"""Graph edge connecting two vertices.

An :class:`Edge` is an immutable value object representing a connection between two vertices.
Edges may be directed or undirected and may carry an optional numeric weight, a human-readable
label, and an arbitrary attribute mapping.

Identity semantics
------------------
Two edges are considered **equal** when they share the same structural identity: ``(source,
target, directed)``.  Weight, label, and extra attributes are *descriptive* — they do not affect
equality or hashing.  This mirrors graph-theoretic convention where an edge is identified by its
endpoints and orientation, not by its annotations.

Immutability
------------
:class:`Edge` is a **frozen** dataclass with ``__slots__``.  Once created, its fields cannot be
reassigned.  The *attrs* mapping is exposed as a read-only :class:`~types.MappingProxyType` so
callers cannot mutate it in place either. To "update" an edge, create a new instance — idiomatic
for frozen dataclasses and compatible with use as ``dict`` keys and ``set`` members.

Backward compatibility
----------------------
The previous API exposed ``vertex1`` and ``vertex2`` field names.  These are retained as
**read-only property aliases** for ``source`` and ``target`` respectively.  New code should
prefer ``source`` / ``target``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .utilities import _freeze_attrs


@dataclass(frozen=True, slots=True)
class Edge:
    """Immutable edge between two vertices.

    An undirected edge is a *line*; a directed edge is an *arc*.  Both flavors support optional
    weights, labels, and free-form attributes.

    :param source: Name of the source (or first) vertex.
    :type source: str
    :param target: Name of the target (or second) vertex.
    :type target: str
    :param directed: Whether this edge is directed.  Defaults to ``False``.
    :type directed: bool
    :param weight: Optional numeric weight.
    :type weight: float | None
    :param label: Optional human-readable label.
    :type label: str | None
    :param attrs: Arbitrary key/value metadata.  Stored internally as an immutable
        :class:`~types.MappingProxyType`.
    :type attrs: MappingProxyType[str, Any]
    """

    source: str
    target: str
    directed: bool = False
    weight: float | None = None
    label: str | None = None
    attrs: MappingProxyType[str, Any] = field(
        default_factory=lambda: MappingProxyType({}),
    )

    # ------------------------------------------------------------------
    # Alternate constructor
    # ------------------------------------------------------------------

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        source: str,
        target: str,
        *,
        directed: bool = False,
        weight: float | None = None,
        label: str | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> Edge:
        """Build an :class:`Edge`, accepting a plain ``dict`` for *attrs*.

        This factory freezes the provided *attrs* dict into a read-only
        :class:`~types.MappingProxyType` so callers don't need to wrap it themselves.

        :param source: Name of the source vertex.
        :type source: str
        :param target: Name of the target vertex.
        :type target: str
        :param directed: Whether the edge is directed.
        :type directed: bool
        :param weight: Optional numeric weight.
        :type weight: float | None
        :param label: Optional human-readable label.
        :type label: str | None
        :param attrs: Mutable attribute dict (will be frozen).
        :type attrs: dict[str, Any] | None
        :return: A new :class:`Edge` instance.
        :rtype: Edge
        """
        return cls(
            source=source,
            target=target,
            directed=directed,
            weight=weight,
            label=label,
            attrs=_freeze_attrs(attrs),
        )

    # ------------------------------------------------------------------
    # Backward-compatible aliases
    # ------------------------------------------------------------------

    @property
    def vertex1(self) -> str:
        """Alias for :attr:`source` (backward compatibility).

        .. deprecated::
            Use :attr:`source` instead.

        :return: Source vertex name.
        :rtype: str
        """
        return self.source

    @property
    def vertex2(self) -> str:
        """Alias for :attr:`target` (backward compatibility).

        .. deprecated::
            Use :attr:`target` instead.

        :return: Target vertex name.
        :rtype: str
        """
        return self.target

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    def has_weight(self) -> bool:
        """Return whether this edge carries a weight.

        :return: ``True`` if :attr:`weight` is not ``None``.
        :rtype: bool
        """
        return self.weight is not None

    def is_self_loop(self) -> bool:
        """Return whether this edge connects a vertex to itself.

        :return: ``True`` if :attr:`source` equals :attr:`target`.
        :rtype: bool
        """
        return self.source == self.target

    # ------------------------------------------------------------------
    # Identity — equality and hashing on structural triple only
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Return ``True`` if *other* has the same structural identity.

        Structural identity is the tuple ``(source, target, directed)``. Weight, label, and attrs
        are **not** considered.

        :param other: Object to compare against.
        :type other: object
        :return: ``True`` if structurally equal.
        :rtype: bool
        """
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            self.source == other.source
            and self.target == other.target
            and self.directed == other.directed
        )

    def __hash__(self) -> int:
        """Return a hash based on structural identity.

        :return: Hash of ``(source, target, directed)``.
        :rtype: int
        """
        return hash((self.source, self.target, self.directed))

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        :return: String like ``Edge('A' -> 'B', weight=3.0)``.
        :rtype: str
        """
        arrow = "->" if self.directed else "--"
        parts = [f"Edge('{self.source}' {arrow} '{self.target}'"]
        if self.weight is not None:
            parts.append(f"weight={self.weight}")
        if self.label is not None:
            parts.append(f"label={self.label!r}")
        if self.attrs:
            parts.append(f"attrs={dict(self.attrs)}")
        return ", ".join(parts) + ")"

    def __str__(self) -> str:
        """Return a human-readable string.

        :return: String like ``A -> B`` or ``A -- B``.
        :rtype: str
        """
        arrow = "->" if self.directed else "--"
        return f"{self.source} {arrow} {self.target}"
