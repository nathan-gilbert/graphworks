"""Unit tests for :class:`graphworks.edge.Edge`.

Covers construction (direct and via factory), structural identity (equality and hashing),
the ``has_weight`` and ``is_self_loop`` predicates, the backward-compatible
``vertex1``/``vertex2`` aliases, immutable ``attrs``, and string representations.
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from graphworks.edge import Edge

# ---------------------------------------------------------------------------
# Construction — direct instantiation
# ---------------------------------------------------------------------------


class TestEdgeConstruction:
    """Tests for Edge construction and default values."""

    def test_basic_construction(self) -> None:
        """An Edge stores source and target correctly."""
        e = Edge("a", "b")
        assert e.source == "a"
        assert e.target == "b"

    def test_directed_defaults_to_false(self) -> None:
        """The directed flag defaults to False."""
        e = Edge("a", "b")
        assert not e.directed

    def test_weight_defaults_to_none(self) -> None:
        """The weight defaults to None."""
        e = Edge("a", "b")
        assert e.weight is None

    def test_label_defaults_to_none(self) -> None:
        """The label defaults to None."""
        e = Edge("a", "b")
        assert e.label is None

    def test_attrs_defaults_to_empty_mapping(self) -> None:
        """The attrs field defaults to an empty MappingProxyType."""
        e = Edge("a", "b")
        assert e.attrs == {}
        assert isinstance(e.attrs, MappingProxyType)

    def test_explicit_directed(self) -> None:
        """The directed flag can be set to True explicitly."""
        e = Edge("a", "b", True)
        assert e.directed

    def test_explicit_weight(self) -> None:
        """A numeric weight is stored and accessible."""
        e = Edge("a", "b", False, 42.5)
        assert e.weight == pytest.approx(42.5)

    def test_explicit_label(self) -> None:
        """A label string is stored and accessible."""
        e = Edge("a", "b", label="highway")
        assert e.label == "highway"

    def test_explicit_attrs(self) -> None:
        """A MappingProxyType attrs is stored and accessible."""
        attrs = MappingProxyType({"color": "red", "capacity": 10})
        e = Edge("a", "b", attrs=attrs)
        assert e.attrs["color"] == "red"
        assert e.attrs["capacity"] == 10


# ---------------------------------------------------------------------------
# Construction — factory method
# ---------------------------------------------------------------------------


class TestEdgeCreateFactory:
    """Tests for the Edge.create() alternate constructor."""

    def test_create_basic(self) -> None:
        """Edge.create builds a valid edge with defaults."""
        e = Edge.create("x", "y")
        assert e.source == "x"
        assert e.target == "y"
        assert not e.directed
        assert e.weight is None
        assert e.label is None
        assert e.attrs == {}

    def test_create_with_plain_dict_attrs(self) -> None:
        """Edge.create freezes a plain dict into a MappingProxyType."""
        e = Edge.create("x", "y", attrs={"color": "blue"})
        assert e.attrs["color"] == "blue"
        assert isinstance(e.attrs, MappingProxyType)

    def test_create_with_none_attrs(self) -> None:
        """Edge.create with attrs=None yields an empty mapping."""
        e = Edge.create("x", "y", attrs=None)
        assert e.attrs == {}
        assert isinstance(e.attrs, MappingProxyType)

    def test_create_with_all_fields(self) -> None:
        """Edge.create accepts all keyword arguments."""
        e = Edge.create(
            "a",
            "b",
            directed=True,
            weight=3.14,
            label="bridge",
            attrs={"toll": 5},
        )
        assert e.source == "a"
        assert e.target == "b"
        assert e.directed
        assert e.weight == pytest.approx(3.14)
        assert e.label == "bridge"
        assert e.attrs["toll"] == 5

    def test_create_does_not_mutate_original_dict(self) -> None:
        """Mutating the input dict after create() has no effect on the Edge."""
        raw = {"key": "original"}
        e = Edge.create("a", "b", attrs=raw)
        raw["key"] = "mutated"
        assert e.attrs["key"] == "original"


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


class TestEdgeImmutability:
    """Tests that Edge instances are truly frozen."""

    def test_cannot_set_source(self) -> None:
        """Attempting to reassign source raises an error."""
        e = Edge("a", "b")
        with pytest.raises(AttributeError):
            e.source = "z"  # type: ignore[misc]

    def test_cannot_set_weight(self) -> None:
        """Attempting to reassign weight raises an error."""
        e = Edge("a", "b")
        with pytest.raises(AttributeError):
            e.weight = 99.0  # type: ignore[misc]

    def test_cannot_mutate_attrs(self) -> None:
        """Attempting to set a key on attrs raises a TypeError."""
        e = Edge.create("a", "b", attrs={"color": "red"})
        with pytest.raises(TypeError):
            e.attrs["color"] = "blue"  # type: ignore[index]

    def test_cannot_add_new_attr(self) -> None:
        """Attempting to add a new key to attrs raises a TypeError."""
        e = Edge("a", "b")
        with pytest.raises(TypeError):
            e.attrs["new_key"] = "value"  # type: ignore[index]


# ---------------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------------


class TestEdgeBackwardCompat:
    """Tests for vertex1/vertex2 property aliases."""

    def test_vertex1_aliases_source(self) -> None:
        """vertex1 returns the same value as source."""
        e = Edge("a", "b")
        assert e.vertex1 == e.source

    def test_vertex2_aliases_target(self) -> None:
        """vertex2 returns the same value as target."""
        e = Edge("a", "b")
        assert e.vertex2 == e.target

    def test_vertex1_read_only(self) -> None:
        """vertex1 cannot be assigned to."""
        e = Edge("a", "b")
        with pytest.raises((AttributeError, TypeError)):
            e.vertex1 = "z"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Predicates
# ---------------------------------------------------------------------------


class TestEdgeHasWeight:
    """Tests for the has_weight predicate."""

    def test_no_weight_returns_false(self) -> None:
        """has_weight() is False when weight is None."""
        e = Edge("a", "b")
        assert not e.has_weight()

    def test_with_weight_returns_true(self) -> None:
        """has_weight() is True when a weight is set."""
        e = Edge("a", "b", True, 50.0)
        assert e.has_weight()

    def test_zero_weight_returns_true(self) -> None:
        """A weight of 0.0 is still considered 'has weight'."""
        e = Edge("a", "b", False, 0.0)
        assert e.has_weight()

    def test_negative_weight_returns_true(self) -> None:
        """A negative weight is still considered 'has weight'."""
        e = Edge("a", "b", False, -1.5)
        assert e.has_weight()


class TestEdgeIsSelfLoop:
    """Tests for the is_self_loop predicate."""

    def test_self_loop_true(self) -> None:
        """is_self_loop returns True when source equals target."""
        e = Edge("a", "a")
        assert e.is_self_loop()

    def test_not_self_loop(self) -> None:
        """is_self_loop returns False for distinct endpoints."""
        e = Edge("a", "b")
        assert not e.is_self_loop()

    def test_directed_self_loop(self) -> None:
        """A directed self-loop is still a self-loop."""
        e = Edge("x", "x", directed=True)
        assert e.is_self_loop()


# ---------------------------------------------------------------------------
# Structural identity — equality
# ---------------------------------------------------------------------------


class TestEdgeEquality:
    """Tests for Edge equality based on structural identity.

    Equality uses ``(source, target, directed)`` only.  Weight, label,
    and attrs are ignored.
    """

    def test_equal_edges(self) -> None:
        """Two Edges with the same structural triple are equal."""
        assert Edge("A", "B") == Edge("A", "B")

    def test_equal_ignores_weight(self) -> None:
        """Edges with different weights but same structure are equal."""
        assert Edge("a", "b", False, 1.0) == Edge("a", "b", False, 2.0)

    def test_equal_ignores_label(self) -> None:
        """Edges with different labels but same structure are equal."""
        assert Edge("a", "b", label="x") == Edge("a", "b", label="y")

    def test_equal_ignores_attrs(self) -> None:
        """Edges with different attrs but same structure are equal."""
        e1 = Edge.create("a", "b", attrs={"k": 1})
        e2 = Edge.create("a", "b", attrs={"k": 2})
        assert e1 == e2

    def test_direction_matters_for_equality(self) -> None:
        """Edge("A","B") != Edge("B","A") due to vertex ordering."""
        assert Edge("A", "B") != Edge("B", "A")

    def test_directed_flag_matters_for_equality(self) -> None:
        """Same endpoints but different directed flag are not equal."""
        assert Edge("a", "b", directed=False) != Edge("a", "b", directed=True)

    def test_not_equal_to_non_edge(self) -> None:
        """Comparing an Edge to a non-Edge returns NotImplemented."""
        e = Edge("a", "b")
        assert e != "not an edge"
        assert e != 42
        assert e != ("a", "b")

    def test_not_equal_to_none(self) -> None:
        """Comparing an Edge to None is False."""
        e = Edge("a", "b")
        assert e != None  # noqa: E711


# ---------------------------------------------------------------------------
# Structural identity — hashing
# ---------------------------------------------------------------------------


class TestEdgeHashing:
    """Tests for Edge hash behaviour based on structural identity."""

    def test_equal_edges_same_hash(self) -> None:
        """Structurally equal edges have the same hash."""
        assert hash(Edge("a", "b")) == hash(Edge("a", "b"))

    def test_different_weight_same_hash(self) -> None:
        """Edges differing only in weight share a hash."""
        e1 = Edge("a", "b", False, 1.0)
        e2 = Edge("a", "b", False, 99.0)
        assert hash(e1) == hash(e2)

    def test_usable_as_dict_key(self) -> None:
        """Edges can serve as dictionary keys."""
        e = Edge("a", "b")
        d = {e: "found"}
        assert d[Edge("a", "b")] == "found"

    def test_usable_in_set(self) -> None:
        """Duplicate structural edges collapse in a set."""
        s = {Edge("a", "b"), Edge("a", "b"), Edge("a", "b", False, 5.0)}
        assert len(s) == 1

    def test_different_edges_in_set(self) -> None:
        """Structurally different edges remain distinct in a set."""
        s = {Edge("a", "b"), Edge("b", "a"), Edge("a", "b", directed=True)}
        assert len(s) == 3

    def test_directed_vs_undirected_different_hash(self) -> None:
        """Same endpoints but different directed flag have different hashes."""
        h1 = hash(Edge("a", "b", directed=False))
        h2 = hash(Edge("a", "b", directed=True))
        # Hash collision is theoretically possible but extremely unlikely
        assert h1 != h2


# ---------------------------------------------------------------------------
# String representations
# ---------------------------------------------------------------------------


class TestEdgeRepr:
    """Tests for __repr__ and __str__."""

    def test_repr_undirected(self) -> None:
        """repr of an undirected edge uses '--' arrow."""
        e = Edge("A", "B")
        r = repr(e)
        assert "A" in r
        assert "B" in r
        assert "--" in r

    def test_repr_directed(self) -> None:
        """repr of a directed edge uses '->' arrow."""
        e = Edge("A", "B", directed=True)
        r = repr(e)
        assert "->" in r

    def test_repr_includes_weight(self) -> None:
        """repr includes the weight when present."""
        e = Edge("A", "B", weight=3.5)
        assert "3.5" in repr(e)

    def test_repr_includes_label(self) -> None:
        """repr includes the label when present."""
        e = Edge("A", "B", label="highway")
        assert "highway" in repr(e)

    def test_repr_includes_attrs(self) -> None:
        """repr includes attrs when non-empty."""
        e = Edge.create("A", "B", attrs={"color": "red"})
        r = repr(e)
        assert "color" in r
        assert "red" in r

    def test_repr_minimal(self) -> None:
        """repr omits weight, label, attrs when they are defaults."""
        e = Edge("A", "B")
        r = repr(e)
        assert "weight" not in r
        assert "label" not in r
        assert "attrs" not in r

    def test_str_undirected(self) -> None:
        """str of an undirected edge is 'source -- target'."""
        e = Edge("A", "B")
        assert str(e) == "A -- B"

    def test_str_directed(self) -> None:
        """str of a directed edge is 'source -> target'."""
        e = Edge("A", "B", directed=True)
        assert str(e) == "A -> B"
