"""Unit tests for :class:`graphworks.edge.Edge`.

:author: Nathan Gilbert
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from graphworks.edge import Edge


class TestEdgeConstruction:
    """Tests for Edge construction and default values."""

    def test_basic_construction(self) -> None:
        e = Edge("a", "b")
        assert e.source == "a"
        assert e.target == "b"

    def test_directed_defaults_to_false(self) -> None:
        assert not Edge("a", "b").directed

    def test_weight_defaults_to_none(self) -> None:
        assert Edge("a", "b").weight is None

    def test_label_defaults_to_none(self) -> None:
        assert Edge("a", "b").label is None

    def test_attrs_defaults_to_empty_mapping(self) -> None:
        e = Edge("a", "b")
        assert e.attrs == {}
        assert isinstance(e.attrs, MappingProxyType)

    def test_explicit_directed(self) -> None:
        assert Edge("a", "b", True).directed

    def test_explicit_weight(self) -> None:
        assert Edge("a", "b", False, 42.5).weight == pytest.approx(42.5)

    def test_explicit_label(self) -> None:
        assert Edge("a", "b", label="highway").label == "highway"

    def test_explicit_attrs(self) -> None:
        attrs = MappingProxyType({"color": "red", "capacity": 10})
        e = Edge("a", "b", attrs=attrs)
        assert e.attrs["color"] == "red"


class TestEdgeCreateFactory:
    """Tests for the Edge.create() alternate constructor."""

    def test_create_basic(self) -> None:
        e = Edge.create("x", "y")
        assert e.source == "x"
        assert e.target == "y"
        assert not e.directed
        assert e.weight is None

    def test_create_freezes_dict(self) -> None:
        e = Edge.create("x", "y", attrs={"color": "blue"})
        assert isinstance(e.attrs, MappingProxyType)

    def test_create_copies_dict(self) -> None:
        raw = {"key": "original"}
        e = Edge.create("a", "b", attrs=raw)
        raw["key"] = "mutated"
        assert e.attrs["key"] == "original"

    def test_create_all_fields(self) -> None:
        e = Edge.create("a", "b", directed=True, weight=3.14, label="bridge", attrs={"toll": 5})
        assert e.directed
        assert e.weight == pytest.approx(3.14)
        assert e.label == "bridge"
        assert e.attrs["toll"] == 5


class TestEdgeImmutability:
    """Tests that Edge instances are truly frozen."""

    def test_cannot_set_source(self) -> None:
        with pytest.raises(AttributeError):
            Edge("a", "b").source = "z"  # noqa # type: ignore[misc]

    def test_cannot_mutate_attrs(self) -> None:
        e = Edge.create("a", "b", attrs={"color": "red"})
        with pytest.raises(TypeError):
            e.attrs["color"] = "blue"  # type: ignore[index]


class TestEdgePredicates:
    """Tests for has_weight and is_self_loop."""

    def test_no_weight(self) -> None:
        assert not Edge("a", "b").has_weight()

    def test_has_weight(self) -> None:
        assert Edge("a", "b", False, 50.0).has_weight()

    def test_zero_weight_counts(self) -> None:
        assert Edge("a", "b", False, 0.0).has_weight()

    def test_self_loop(self) -> None:
        assert Edge("a", "a").is_self_loop()

    def test_not_self_loop(self) -> None:
        assert not Edge("a", "b").is_self_loop()


class TestEdgeEquality:
    """Tests for structural identity equality."""

    def test_equal_edges(self) -> None:
        assert Edge("A", "B") == Edge("A", "B")

    def test_ignores_weight(self) -> None:
        assert Edge("a", "b", False, 1.0) == Edge("a", "b", False, 2.0)

    def test_ignores_label(self) -> None:
        assert Edge("a", "b", label="x") == Edge("a", "b", label="y")

    def test_ignores_attrs(self) -> None:
        assert Edge.create("a", "b", attrs={"k": 1}) == Edge.create("a", "b", attrs={"k": 2})

    def test_endpoint_order_matters(self) -> None:
        assert Edge("A", "B") != Edge("B", "A")

    def test_directed_flag_matters(self) -> None:
        assert Edge("a", "b", directed=False) != Edge("a", "b", directed=True)

    def test_not_equal_to_non_edge(self) -> None:
        assert Edge("a", "b") != "not an edge"


class TestEdgeHashing:
    """Tests for structural identity hashing."""

    def test_equal_edges_same_hash(self) -> None:
        assert hash(Edge("a", "b")) == hash(Edge("a", "b"))

    def test_usable_as_dict_key(self) -> None:
        d = {Edge("a", "b"): "found"}
        assert d[Edge("a", "b")] == "found"

    def test_deduplication_in_set(self) -> None:
        s = {Edge("a", "b"), Edge("a", "b"), Edge("a", "b", False, 5.0)}
        assert len(s) == 1

    def test_different_edges_in_set(self) -> None:
        s = {Edge("a", "b"), Edge("b", "a"), Edge("a", "b", directed=True)}
        assert len(s) == 3


class TestEdgeDisplay:
    """Tests for __repr__ and __str__."""

    def test_repr_undirected(self) -> None:
        assert "--" in repr(Edge("A", "B"))

    def test_repr_directed(self) -> None:
        assert "->" in repr(Edge("A", "B", directed=True))

    def test_repr_includes_weight(self) -> None:
        assert "3.5" in repr(Edge("A", "B", weight=3.5))

    def test_repr_minimal(self) -> None:
        r = repr(Edge("A", "B"))
        assert "weight" not in r
        assert "label" not in r
        assert "attrs" not in r

    def test_str_undirected(self) -> None:
        assert str(Edge("A", "B")) == "A -- B"

    def test_str_directed(self) -> None:
        assert str(Edge("A", "B", directed=True)) == "A -> B"
