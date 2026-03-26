"""Graph vertex (node) with optional label and metadata.

A :class:`Vertex` is an immutable value object representing a single node in a graph.  Each
vertex has a unique *name* that serves as its identity key, an optional human-readable *label* (
defaulting to the name), and an arbitrary attribute mapping for user-defined metadata.

Identity semantics
------------------
Two vertices are considered **equal** when they share the same :attr:`name`. The :attr:`label`
and :attr:`attrs` fields are *descriptive* — they do not affect equality or hashing.  This
mirrors graph-theoretic convention: a vertex is identified by its name alone, regardless of any
annotations attached to it.

Immutability
------------
:class:`Vertex` is a **frozen** dataclass with ``__slots__``.  Once created, its fields cannot be
reassigned.  The *attrs* mapping is exposed as a read-only :class:`~types.MappingProxyType` so
callers cannot mutate it in place either. To "update" a vertex, create a new instance — idiomatic
for frozen dataclasses and compatible with use as ``dict`` keys and ``set`` members.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True, slots=True)
class Vertex:
    """Immutable graph vertex (node).

    A vertex is the fundamental unit of a graph.  It carries a unique :attr:`name` used as the
    identity key, an optional :attr:`label` for display purposes, and a free-form :attr:`attrs`
    mapping for arbitrary metadata (e.g. color, coordinates, community ID).

    :param name: Unique identifier for this vertex.
    :type name: str
    :param label: Human-readable display name.  Defaults to :attr:`name` when ``None`` is passed.
    :type label: str | None
    :param attrs: Arbitrary key/value metadata.  Stored internally as an immutable
        :class:`~types.MappingProxyType`.
    :type attrs: MappingProxyType[str, Any]
    """

    name: str
    label: str | None = None
    attrs: MappingProxyType[str, Any] = field(
        default_factory=lambda: MappingProxyType({}),
    )

    @classmethod
    def create(
        cls,
        name: str,
        *,
        label: str | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> Vertex:
        """Build a :class:`Vertex`, accepting a plain ``dict`` for *attrs*.

        This factory freezes the provided *attrs* dict into a read-only
        :class:`~types.MappingProxyType` so callers don't need to wrap it themselves.

        :param name: Unique identifier for this vertex.
        :type name: str
        :param label: Human-readable display name.
        :type label: str | None
        :param attrs: Mutable attribute dict (will be defensively copied and frozen).
        :type attrs: dict[str, Any] | None
        :return: A new :class:`Vertex` instance.
        :rtype: Vertex
        """
        return cls(
            name=name,
            label=label,
            attrs=_freeze_attrs(attrs),
        )

    @property
    def display_name(self) -> str:
        """Return the label if set, otherwise the name.

        Convenience property for rendering and export code that needs a single human-readable
        string for this vertex.

        :return: The :attr:`label` if not ``None``, else :attr:`name`.
        :rtype: str
        """
        return self.label if self.label is not None else self.name

    # ------------------------------------------------------------------
    # Identity — equality and hashing on name only
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Return ``True`` if *other* is a :class:`Vertex` with the same name.

        Only :attr:`name` is compared.  :attr:`label` and :attr:`attrs` are descriptive and do
        not affect identity.

        :param other: Object to compare against.
        :type other: object
        :return: ``True`` if names match.
        :rtype: bool
        """
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash based on :attr:`name` only.

        :return: Hash of the vertex name.
        :rtype: int
        """
        return hash(self.name)

    # ------------------------------------------------------------------
    # Ordering — enables sorted() on vertex collections
    # ------------------------------------------------------------------

    def __lt__(self, other: object) -> bool:
        """Return ``True`` if this vertex's name sorts before *other*'s.

        Supports ``sorted()`` and ``min()``/``max()`` on vertex collections without requiring a
        ``key=`` function.

        :param other: Object to compare against.
        :type other: object
        :return: ``True`` if ``self.name < other.name``.
        :rtype: bool
        """
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.name < other.name

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly representation.

        :return: String like ``Vertex('A')`` or ``Vertex('A', label='Alice', attrs={'color':
            'red'})``.
        :rtype: str
        """
        parts = [f"Vertex({self.name!r}"]
        if self.label is not None:
            parts.append(f"label={self.label!r}")
        if self.attrs:
            parts.append(f"attrs={dict(self.attrs)}")
        return ", ".join(parts) + ")"

    def __str__(self) -> str:
        """Return the display name of this vertex.

        :return: The :attr:`label` if set, otherwise :attr:`name`.
        :rtype: str
        """
        return self.display_name
