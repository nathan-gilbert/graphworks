#!/usr/bin/env python3
"""Graphworks demo — a rich tour of the library's core features.

Run with::

    uv run demo

Or directly::

    uv run python examples/demo.py

Requires the ``[viz]`` optional extra::

    uv sync --extra viz

This script is **not** shipped with the library.  It lives in the ``examples/`` directory and is
excluded from both the sdist and wheel builds.
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from graphworks.algorithms import (
    breadth_first_search,
    degree_sequence,
    density,
    depth_first_search,
    diameter,
    find_all_paths,
    find_isolated_vertices,
    find_path,
    is_complete,
    is_connected,
    is_dag,
    is_regular,
    is_simple,
    topological,
    vertex_degree,
)
from graphworks.graph import Graph
from graphworks.vertex import Vertex

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    """Print a Rich rule as a section divider.

    :param title: Section heading text.
    :type title: str
    :return: Nothing.
    :rtype: None
    """
    console.print()
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print()


def _kv(key: str, value: object) -> None:
    """Print a key/value pair with Rich markup.

    :param key: Label.
    :type key: str
    :param value: Value to display.
    :type value: object
    :return: Nothing.
    :rtype: None
    """
    console.print(f"  [dim]{key:<16}[/dim] {value}")


def _graph_panel(graph: Graph, title: str, border_style: str = "blue") -> None:
    """Display a graph as a Rich Tree inside a Panel.

    This gives a clear, readable adjacency-list visualisation that works for
    both directed and undirected graphs of any size — no external layout
    engine required.

    :param graph: The graph to display.
    :type graph: Graph
    :param title: Panel title.
    :type title: str
    :param border_style: Rich border colour.
    :type border_style: str
    :return: Nothing.
    :rtype: None
    """
    arrow = "→" if graph.directed else "—"
    tree = Tree(f"[bold]{title}[/bold]")
    for v in sorted(graph.vertices()):
        neighbours = graph.neighbors(v)
        if neighbours:
            label = f"[green]{v}[/green] {arrow} " + ", ".join(
                f"[cyan]{n}[/cyan]" for n in neighbours
            )
        else:
            label = f"[green]{v}[/green] [dim](no edges)[/dim]"
        tree.add(label)
    console.print(Panel(tree, border_style=border_style))


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------


def demo_construction() -> Graph:
    """Demonstrate graph construction and display.

    :return: The JSON-constructed graph used in subsequent demos.
    :rtype: Graph
    """
    _section("1 · Graph construction")

    json_def = {
        "label": "social network",
        "directed": False,
        "graph": {
            "Alice": ["Bob", "Carol"],
            "Bob": ["Alice", "Dave"],
            "Carol": ["Alice", "Dave"],
            "Dave": ["Bob", "Carol", "Eve"],
            "Eve": ["Dave"],
        },
    }
    graph = Graph(input_graph=json.dumps(json_def))
    _kv("label", graph.label)
    _kv("vertices", graph.order)
    _kv("edges", graph.size)
    _kv("directed", graph.directed)

    console.print()
    _graph_panel(graph, "social network")

    # Matrix construction
    console.print()
    matrix = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    matrix_graph = Graph(input_matrix=matrix)
    _kv("from matrix", f"{matrix_graph.order} vertices, {matrix_graph.size} edges")

    # Programmatic construction with Vertex objects
    manual = Graph("manual")
    manual.add_vertex(Vertex.create("X", label="Entry"))
    manual.add_vertex(Vertex.create("Y", label="Middle"))
    manual.add_vertex(Vertex.create("Z", label="Exit"))
    manual.add_edge("X", "Y")
    manual.add_edge("Y", "Z")
    _kv("programmatic", f"{manual.order} vertices, {manual.size} edges")

    # Show that Vertex metadata survives
    for name in manual.vertices():
        v = manual.vertex(name)
        if v is not None:
            _kv(f"  {name}", f"display_name={v.display_name!r}")

    # Weighted edge construction
    weighted = Graph("routes", weighted=True)
    weighted.add_edge("Denver", "SLC", weight=525.0, label="I-70/I-15")
    weighted.add_edge("SLC", "Boise", weight=340.0, label="I-84")
    e = weighted.edge("Denver", "SLC")
    if e is not None:
        _kv("weighted edge", f"{e} (weight={e.weight}, label={e.label!r})")

    return graph


def demo_properties(graph: Graph) -> None:
    """Show structural property queries in a Rich table.

    :param graph: An undirected graph to inspect.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("2 · Structural properties")

    props = {
        "connected": is_connected(graph),
        "complete": is_complete(graph),
        "simple": is_simple(graph),
        "regular": is_regular(graph),
        "density": f"{density(graph):.4f}",
        "diameter": diameter(graph),
        "deg sequence": degree_sequence(graph),
        "isolated": find_isolated_vertices(graph) or "(none)",
    }

    table = Table(title="Graph Properties", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    for k, v in props.items():
        val_str = str(v)
        style = ""
        if isinstance(v, bool):
            style = "green" if v else "red"
            val_str = "✓" if v else "✗"
        table.add_row(k, Text(val_str, style=style))
    console.print(table)


def demo_degrees(graph: Graph) -> None:
    """Display per-vertex degree information in a table.

    :param graph: An undirected graph to inspect.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("3 · Vertex degrees")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Vertex", style="green")
    table.add_column("Degree", justify="right")
    table.add_column("Neighbours")
    for v in sorted(graph.vertices()):
        deg = vertex_degree(graph, v)
        nbrs = ", ".join(graph.neighbors(v)) or "(none)"
        table.add_row(v, str(deg), nbrs)
    console.print(table)


def demo_traversal(graph: Graph) -> None:
    """Run BFS and DFS from a starting vertex.

    :param graph: An undirected graph to traverse.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("4 · Traversals")

    start = graph.vertices()[0]
    bfs = breadth_first_search(graph, start)
    dfs = depth_first_search(graph, start)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Algorithm", style="cyan")
    table.add_column(f"From '{start}'")
    table.add_row("BFS", " → ".join(bfs))
    table.add_row("DFS", " → ".join(dfs))
    console.print(table)


def demo_paths(graph: Graph) -> None:
    """Demonstrate path-finding between two vertices.

    :param graph: An undirected graph to search.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("5 · Path finding")

    src, dst = "Alice", "Eve"
    single = find_path(graph, src, dst)

    _kv("shortest path", " → ".join(single) if single else "(none)")
    console.print()

    all_paths = find_all_paths(graph, src, dst)
    table = Table(
        title=f"All paths: {src} → {dst}",
        show_header=True,
        header_style="bold",
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Path")
    table.add_column("Length", justify="right")
    for i, p in enumerate(all_paths, 1):
        table.add_row(str(i), " → ".join(p), str(len(p) - 1))
    console.print(table)


def demo_complement(graph: Graph) -> None:
    """Show the complement graph.

    The library's :func:`get_complement` returns a matrix-based graph with
    UUID vertex names (the original names are lost in the matrix round-trip).
    For display purposes we compute the missing edges directly so we can
    show them with the original, human-readable vertex names.

    :param graph: An undirected graph.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("6 · Complement graph")

    verts = sorted(graph.vertices())
    original_edges: set[tuple[str, str]] = set()
    for v in verts:
        for n in graph.neighbors(v):
            edge = (min(v, n), max(v, n))
            original_edges.add(edge)

    complement_edges: list[tuple[str, str]] = []
    for i, v1 in enumerate(verts):
        for v2 in verts[i + 1 :]:
            if (min(v1, v2), max(v1, v2)) not in original_edges:
                complement_edges.append((v1, v2))

    _kv("original edges", len(original_edges))
    _kv("complement edges", len(complement_edges))
    console.print()

    table = Table(
        show_header=True, header_style="bold", title="Complement Edges (missing from original)"
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("From", style="green")
    table.add_column("", justify="center")
    table.add_column("To", style="cyan")
    for i, (v1, v2) in enumerate(complement_edges, 1):
        table.add_row(str(i), v1, "—", v2)
    console.print(table)


def demo_directed() -> None:
    """Demonstrate directed graph features: DAG detection and topological sort.

    :return: Nothing.
    :rtype: None
    """
    _section("7 · Directed graphs")

    dag_def = {
        "directed": True,
        "label": "build pipeline",
        "graph": {
            "lint": [],
            "typecheck": [],
            "compile": ["lint", "typecheck"],
            "test": ["compile"],
            "package": ["test"],
            "deploy": ["package"],
        },
    }
    dag = Graph(input_graph=json.dumps(dag_def))

    _kv("DAG?", is_dag(dag))
    _kv("topo sort", " → ".join(topological(dag)))

    console.print()
    _graph_panel(dag, "build pipeline (DAG)", border_style="green")

    # Cyclic example
    console.print()
    cycle_def = {
        "directed": True,
        "label": "cyclic pipeline",
        "graph": {
            "lint": ["compile"],
            "compile": ["test"],
            "test": ["deploy"],
            "deploy": ["lint"],
        },
    }
    cyclic = Graph(input_graph=json.dumps(cycle_def))
    _kv("cyclic graph", f"DAG? {is_dag(cyclic)}")

    console.print()
    _graph_panel(cyclic, "cyclic pipeline (NOT a DAG)", border_style="red")


def demo_adjacency_matrix(graph: Graph) -> None:
    """Display the adjacency matrix as a Rich table.

    :param graph: A graph to display.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("8 · Adjacency matrix")

    matrix = graph.adjacency_matrix()
    verts = sorted(graph.vertices())

    table = Table(show_header=True, header_style="bold")
    table.add_column("", style="green")
    for v in verts:
        table.add_column(v, justify="center", min_width=3)
    for i, v in enumerate(verts):
        cells = []
        for val in matrix[i]:
            if val:
                cells.append("[bold green]1[/bold green]")
            else:
                cells.append("[dim]·[/dim]")
        table.add_row(v, *cells)
    console.print(table)


def demo_edge_inspection(graph: Graph) -> None:
    """Show the first-class Edge objects stored in the graph.

    :param graph: A graph whose edges to inspect.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("9 · Edge objects")

    table = Table(show_header=True, header_style="bold")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Edge", style="cyan")
    table.add_column("Directed")
    table.add_column("Weight")
    table.add_column("Self-loop")
    for i, e in enumerate(graph.edges(), 1):
        table.add_row(
            str(i),
            str(e),
            "✓" if e.directed else "✗",
            str(e.weight) if e.has_weight() else "—",
            "✓" if e.is_self_loop() else "✗",
        )
    console.print(table)

    # Direct edge lookup
    console.print()
    src, tgt = graph.vertices()[0], graph.vertices()[1]
    e = graph.edge(src, tgt)
    if e is not None:
        _kv("edge lookup", f"graph.edge({src!r}, {tgt!r}) = {e!r}")
    else:
        _kv("edge lookup", f"No edge between {src!r} and {tgt!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all demo sections.

    :return: Nothing.
    :rtype: None
    """
    console.print(
        Panel(
            "[bold]graphworks[/bold] — library demo",
            style="bold blue",
            expand=False,
        )
    )

    graph = demo_construction()
    demo_properties(graph)
    demo_degrees(graph)
    demo_traversal(graph)
    demo_paths(graph)
    demo_complement(graph)
    demo_directed()
    demo_adjacency_matrix(graph)
    demo_edge_inspection(graph)

    console.print()
    console.rule("[bold green]Done![/bold green]")
    console.print(
        "  Explore the source at [link=https://github.com/nathan-gilbert/graphworks]"
        "src/graphworks/[/link]"
    )


if __name__ == "__main__":
    main()
