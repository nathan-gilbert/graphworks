"""Unit tests for :class:`graphworks.vertex.Vertex`."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from graphworks.vertex import Vertex


class TestVertexConstruction:
    def test_basic(self) -> None:
        assert Vertex("a").name == "a"

    def test_label_defaults_to_none(self) -> None:
        assert Vertex("a").label is None

    def test_attrs_defaults_empty(self) -> None:
        v = Vertex("a")
        assert v.attrs == {}
        assert isinstance(v.attrs, MappingProxyType)

    def test_explicit_label(self) -> None:
        assert Vertex("n1", label="Start").label == "Start"

    def test_explicit_attrs(self) -> None:
        attrs = MappingProxyType({"color": "red"})
        assert Vertex("a", attrs=attrs).attrs["color"] == "red"


class TestVertexCreateFactory:
    def test_create_basic(self) -> None:
        v = Vertex.create("x")
        assert v.name == "x"
        assert v.label is None
        assert v.attrs == {}

    def test_create_freezes_dict(self) -> None:
        v = Vertex.create("x", attrs={"color": "blue"})
        assert isinstance(v.attrs, MappingProxyType)

    def test_create_copies_dict(self) -> None:
        raw = {"key": "original"}
        v = Vertex.create("a", attrs=raw)
        raw["key"] = "mutated"
        assert v.attrs["key"] == "original"

    def test_create_all_fields(self) -> None:
        v = Vertex.create("hub", label="Central", attrs={"rank": 1})
        assert v.label == "Central"
        assert v.attrs["rank"] == 1


class TestVertexImmutability:
    def test_cannot_set_name(self) -> None:
        with pytest.raises(AttributeError):
            Vertex("a").name = "z"  # noqa # type: ignore[misc]

    def test_cannot_mutate_attrs(self) -> None:
        v = Vertex.create("a", attrs={"color": "red"})
        with pytest.raises(TypeError):
            v.attrs["color"] = "blue"  # type: ignore[index]


class TestVertexDisplayName:
    def test_falls_back_to_name(self) -> None:
        assert Vertex("node_42").display_name == "node_42"

    def test_uses_label(self) -> None:
        assert Vertex("n1", label="Start").display_name == "Start"

    def test_empty_string_label(self) -> None:
        assert Vertex("n1", label="").display_name == ""


class TestVertexEquality:
    def test_equal_by_name(self) -> None:
        assert Vertex("a") == Vertex("a")

    def test_ignores_label(self) -> None:
        assert Vertex("a", label="foo") == Vertex("a", label="bar")

    def test_ignores_attrs(self) -> None:
        assert Vertex.create("a", attrs={"k": 1}) == Vertex.create("a", attrs={"k": 2})

    def test_different_names(self) -> None:
        assert Vertex("a") != Vertex("b")

    def test_case_sensitive(self) -> None:
        assert Vertex("A") != Vertex("a")

    def test_not_equal_to_string(self) -> None:
        assert Vertex("a") != "a"


class TestVertexHashing:
    def test_same_hash(self) -> None:
        assert hash(Vertex("a")) == hash(Vertex("a"))

    def test_usable_as_dict_key(self) -> None:
        assert {Vertex("a"): "found"}[Vertex("a")] == "found"

    def test_set_dedup(self) -> None:
        assert len({Vertex("a"), Vertex("a"), Vertex("a", label="x")}) == 1


class TestVertexOrdering:
    def test_less_than(self) -> None:
        assert Vertex("a") < Vertex("b")

    def test_sorted(self) -> None:
        result = sorted([Vertex("c"), Vertex("a"), Vertex("b")])
        assert [v.name for v in result] == ["a", "b", "c"]

    def test_lt_non_vertex(self) -> None:
        assert Vertex("a").__lt__("a") is NotImplemented


class TestVertexDisplay:
    def test_repr_name_only(self) -> None:
        assert repr(Vertex("A")) == "Vertex('A')"

    def test_repr_with_label(self) -> None:
        assert "label='Alice'" in repr(Vertex("A", label="Alice"))

    def test_str_uses_display_name(self) -> None:
        assert str(Vertex("n1", label="Start")) == "Start"

    def test_str_falls_back(self) -> None:
        assert str(Vertex("n1")) == "n1"
