"""Unit tests for :class:`graphworks.vertex.Vertex`.

Covers construction (direct and via factory), identity semantics (equality and hashing on name
only), ordering, the ``display_name`` property, immutability guarantees, ``attrs`` isolation,
and string representations.
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from graphworks.vertex import Vertex

# ---------------------------------------------------------------------------
# Construction — direct instantiation
# ---------------------------------------------------------------------------


class TestVertexConstruction:
    """Tests for Vertex construction and default values."""

    def test_basic_construction(self) -> None:
        """A Vertex stores its name correctly."""
        v = Vertex("a")
        assert v.name == "a"

    def test_label_defaults_to_none(self) -> None:
        """The label defaults to None when not provided."""
        v = Vertex("a")
        assert v.label is None

    def test_attrs_defaults_to_empty_mapping(self) -> None:
        """The attrs field defaults to an empty MappingProxyType."""
        v = Vertex("a")
        assert v.attrs == {}
        assert isinstance(v.attrs, MappingProxyType)

    def test_explicit_label(self) -> None:
        """An explicit label string is stored and accessible."""
        v = Vertex("node_1", label="Start Node")
        assert v.label == "Start Node"

    def test_explicit_attrs(self) -> None:
        """A MappingProxyType attrs is stored and accessible."""
        attrs = MappingProxyType({"color": "red", "weight": 5})
        v = Vertex("a", attrs=attrs)
        assert v.attrs["color"] == "red"
        assert v.attrs["weight"] == 5

    def test_all_fields(self) -> None:
        """All fields can be set at once via direct construction."""
        attrs = MappingProxyType({"x": 10, "y": 20})
        v = Vertex("hub", label="Central Hub", attrs=attrs)
        assert v.name == "hub"
        assert v.label == "Central Hub"
        assert v.attrs["x"] == 10


# ---------------------------------------------------------------------------
# Construction — factory method
# ---------------------------------------------------------------------------


class TestVertexCreateFactory:
    """Tests for the Vertex.create() alternate constructor."""

    def test_create_basic(self) -> None:
        """Vertex.create builds a valid vertex with defaults."""
        v = Vertex.create("x")
        assert v.name == "x"
        assert v.label is None
        assert v.attrs == {}

    def test_create_with_plain_dict_attrs(self) -> None:
        """Vertex.create freezes a plain dict into a MappingProxyType."""
        v = Vertex.create("x", attrs={"color": "blue"})
        assert v.attrs["color"] == "blue"
        assert isinstance(v.attrs, MappingProxyType)

    def test_create_with_none_attrs(self) -> None:
        """Vertex.create with attrs=None yields an empty mapping."""
        v = Vertex.create("x", attrs=None)
        assert v.attrs == {}
        assert isinstance(v.attrs, MappingProxyType)

    def test_create_with_all_fields(self) -> None:
        """Vertex.create accepts all keyword arguments."""
        v = Vertex.create("hub", label="Central", attrs={"rank": 1})
        assert v.name == "hub"
        assert v.label == "Central"
        assert v.attrs["rank"] == 1

    def test_create_does_not_mutate_original_dict(self) -> None:
        """Mutating the input dict after create() has no effect on the Vertex."""
        raw = {"key": "original"}
        v = Vertex.create("a", attrs=raw)
        raw["key"] = "mutated"
        assert v.attrs["key"] == "original"


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


class TestVertexImmutability:
    """Tests that Vertex instances are truly frozen."""

    def test_cannot_set_name(self) -> None:
        """Attempting to reassign name raises an error."""
        v = Vertex("a")
        with pytest.raises(AttributeError):
            v.name = "z"  # noqa  # ty:ignore[invalid-assignment]

    def test_cannot_set_label(self) -> None:
        """Attempting to reassign label raises an error."""
        v = Vertex("a", label="original")
        with pytest.raises(AttributeError):
            v.label = "changed"  # noqa  # ty:ignore[invalid-assignment]

    def test_cannot_mutate_attrs(self) -> None:
        """Attempting to set a key on attrs raises a TypeError."""
        v = Vertex.create("a", attrs={"color": "red"})
        with pytest.raises(TypeError):
            v.attrs["color"] = "blue"  # type: ignore[index]

    def test_cannot_add_new_attr(self) -> None:
        """Attempting to add a new key to attrs raises a TypeError."""
        v = Vertex("a")
        with pytest.raises(TypeError):
            v.attrs["new_key"] = "value"  # type: ignore[index]


# ---------------------------------------------------------------------------
# display_name property
# ---------------------------------------------------------------------------


class TestVertexDisplayName:
    """Tests for the display_name derived property."""

    def test_display_name_falls_back_to_name(self) -> None:
        """display_name returns name when label is None."""
        v = Vertex("node_42")
        assert v.display_name == "node_42"

    def test_display_name_uses_label(self) -> None:
        """display_name returns label when it is set."""
        v = Vertex("n1", label="Start")
        assert v.display_name == "Start"

    def test_display_name_with_empty_string_label(self) -> None:
        """An empty-string label is still used (it is not None)."""
        v = Vertex("n1", label="")
        assert v.display_name == ""


# ---------------------------------------------------------------------------
# Identity — equality
# ---------------------------------------------------------------------------


class TestVertexEquality:
    """Tests for Vertex equality based on name only.

    Label and attrs are descriptive and do not affect identity.
    """

    def test_equal_by_name(self) -> None:
        """Two Vertices with the same name are equal."""
        assert Vertex("a") == Vertex("a")

    def test_equal_ignores_label(self) -> None:
        """Vertices with different labels but the same name are equal."""
        assert Vertex("a", label="foo") == Vertex("a", label="bar")

    def test_equal_ignores_attrs(self) -> None:
        """Vertices with different attrs but the same name are equal."""
        v1 = Vertex.create("a", attrs={"k": 1})
        v2 = Vertex.create("a", attrs={"k": 2})
        assert v1 == v2

    def test_different_names_not_equal(self) -> None:
        """Vertices with different names are not equal."""
        assert Vertex("a") != Vertex("b")

    def test_case_sensitive(self) -> None:
        """Vertex names are case-sensitive."""
        assert Vertex("A") != Vertex("a")

    def test_not_equal_to_non_vertex(self) -> None:
        """Comparing a Vertex to a non-Vertex returns NotImplemented."""
        v = Vertex("a")
        assert v != "a"
        assert v != 42

    def test_not_equal_to_none(self) -> None:
        """Comparing a Vertex to None is False."""
        v = Vertex("a")
        assert v != None  # noqa: E711

    def test_not_equal_to_string_of_same_name(self) -> None:
        """A Vertex is not equal to a bare string, even if the name matches."""
        v = Vertex("hello")
        assert v != "hello"


# ---------------------------------------------------------------------------
# Identity — hashing
# ---------------------------------------------------------------------------


class TestVertexHashing:
    """Tests for Vertex hash behaviour based on name only."""

    def test_equal_vertices_same_hash(self) -> None:
        """Vertices with the same name have the same hash."""
        assert hash(Vertex("a")) == hash(Vertex("a"))

    def test_different_label_same_hash(self) -> None:
        """Vertices differing only in label share a hash."""
        assert hash(Vertex("a", label="x")) == hash(Vertex("a", label="y"))

    def test_usable_as_dict_key(self) -> None:
        """Vertices can serve as dictionary keys."""
        v = Vertex("a")
        d = {v: "found"}
        assert d[Vertex("a")] == "found"

    def test_usable_in_set(self) -> None:
        """Duplicate-name vertices collapse in a set."""
        s = {Vertex("a"), Vertex("a"), Vertex("a", label="different")}
        assert len(s) == 1

    def test_different_names_in_set(self) -> None:
        """Vertices with different names remain distinct in a set."""
        s = {Vertex("a"), Vertex("b"), Vertex("c")}
        assert len(s) == 3


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------


class TestVertexOrdering:
    """Tests for __lt__ which enables sorted() on vertex collections."""

    def test_less_than(self) -> None:
        """Vertex 'a' sorts before Vertex 'b'."""
        assert Vertex("a") < Vertex("b")

    def test_not_less_than(self) -> None:
        """Vertex 'b' does not sort before Vertex 'a'."""
        assert not (Vertex("b") < Vertex("a"))

    def test_equal_not_less_than(self) -> None:
        """A Vertex is not less than itself."""
        assert not (Vertex("a") < Vertex("a"))

    def test_sorted_collection(self) -> None:
        """sorted() on a list of Vertices produces name-alphabetical order."""
        vertices = [Vertex("c"), Vertex("a"), Vertex("b")]
        result = sorted(vertices)
        assert [v.name for v in result] == ["a", "b", "c"]

    def test_min_and_max(self) -> None:
        """min() and max() work on Vertex collections."""
        vertices = [Vertex("c"), Vertex("a"), Vertex("b")]
        assert min(vertices).name == "a"
        assert max(vertices).name == "c"

    def test_lt_with_non_vertex_returns_not_implemented(self) -> None:
        """Comparing a Vertex to a non-Vertex via < returns NotImplemented."""
        v = Vertex("a")
        assert v.__lt__("a") is NotImplemented


# ---------------------------------------------------------------------------
# String representations
# ---------------------------------------------------------------------------


class TestVertexRepr:
    """Tests for __repr__ and __str__."""

    def test_repr_name_only(self) -> None:
        """repr with just a name is compact."""
        v = Vertex("A")
        assert repr(v) == "Vertex('A')"

    def test_repr_with_label(self) -> None:
        """repr includes label when present."""
        v = Vertex("A", label="Alice")
        r = repr(v)
        assert "Vertex('A'" in r
        assert "label='Alice'" in r

    def test_repr_with_attrs(self) -> None:
        """repr includes attrs when non-empty."""
        v = Vertex.create("A", attrs={"color": "red"})
        r = repr(v)
        assert "color" in r
        assert "red" in r

    def test_repr_minimal_omits_defaults(self) -> None:
        """repr omits label and attrs when they are defaults."""
        v = Vertex("A")
        r = repr(v)
        assert "label" not in r
        assert "attrs" not in r

    def test_str_uses_display_name_fallback(self) -> None:
        """str() returns name when label is not set."""
        v = Vertex("node_1")
        assert str(v) == "node_1"

    def test_str_uses_label(self) -> None:
        """str() returns label when it is set."""
        v = Vertex("n1", label="Start")
        assert str(v) == "Start"
