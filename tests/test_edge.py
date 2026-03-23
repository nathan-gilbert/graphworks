"""
tests.test_edge
~~~~~~~~~~~~~~~

Unit tests for :class:`graphworks.edge.Edge`.

:author: Nathan Gilbert
"""

from __future__ import annotations

import pytest

from graphworks.edge import Edge


class TestEdgeConstruction:
    """Tests for Edge construction and default values."""

    def test_basic_construction(self) -> None:
        """An Edge stores vertex1 and vertex2 correctly."""
        e = Edge("a", "b")
        assert e.vertex1 == "a"
        assert e.vertex2 == "b"

    def test_directed_defaults_to_false(self) -> None:
        """The directed flag defaults to False."""
        e = Edge("a", "b")
        assert not e.directed

    def test_weight_defaults_to_none(self) -> None:
        """The weight defaults to None."""
        e = Edge("a", "b")
        assert e.weight is None

    def test_explicit_directed(self) -> None:
        """The directed flag can be set to True explicitly."""
        e = Edge("a", "b", True)
        assert e.directed

    def test_explicit_weight(self) -> None:
        """A numeric weight is stored and accessible."""
        e = Edge("a", "b", False, 42.5)
        assert e.weight == pytest.approx(42.5)


class TestEdgeHasWeight:
    """Tests for the has_weight predicate."""

    def test_no_weight_returns_false(self) -> None:
        """has_weight() is False when weight is None."""
        e = Edge("a", "b", False)
        assert not e.has_weight()

    def test_with_weight_returns_true(self) -> None:
        """has_weight() is True when a weight is set."""
        e = Edge("a", "b", True, 50.0)
        assert e.has_weight()

    def test_zero_weight_returns_true(self) -> None:
        """A weight of 0.0 is still considered 'has weight'."""
        e = Edge("a", "b", False, 0.0)
        assert e.has_weight()


class TestEdgeEquality:
    """Tests for Edge dataclass equality semantics."""

    def test_equal_edges(self) -> None:
        """Two Edge instances with the same fields are equal."""
        assert Edge("A", "B") == Edge("A", "B")

    def test_direction_matters(self) -> None:
        """Edge("A","B") != Edge("B","A") due to vertex ordering."""
        assert Edge("A", "B") != Edge("B", "A")

    def test_weight_affects_equality(self) -> None:
        """Edges with different weights are not equal."""
        assert Edge("a", "b", False, 1.0) != Edge("a", "b", False, 2.0)
