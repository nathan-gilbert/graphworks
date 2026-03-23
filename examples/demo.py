#!/usr/bin/env python3
"""Graphworks demo — a rich tour of the library's core features.

Run with::

    uv run demo

Or directly::

    uv run python examples/demo.py

Requires the ``[viz]`` optional extra::

    uv sync --extra viz

This script is **not** shipped with the library.  It lives in the ``examples/``
directory and is excluded from both the sdist and wheel builds.
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
    get_complement,
    is_complete,
    is_connected,
    is_dag,
    is_regular,
    is_simple,
    topological,
    vertex_degree,
)
from graphworks.graph import Graph

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
    arrow = "→" if graph.is_directed() else "—"
    tree = Tree(f"[bold]{title}[/bold]")
    for v in sorted(graph.vertices()):
        neighbours = graph.get_neighbors(v)
        if neighbours:
            label = f"[green]{v}[/green] {arrow} " + ", ".join(
                f"[cyan]{n}[/cyan]" for n in neighbours
            )
        else:
            label = f"[green]{v}[/green] [dim](no edges)[/dim]"
        tree.add(label)
    console.print(Panel(tree, border_style=border_style))


def _edge_table(graph: Graph) -> None:
    """Display edges in a compact Rich table.

    :param graph: The graph whose edges to display.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    edges = graph.edges()
    if not edges:
        console.print("  [dim](no edges)[/dim]")
        return
    arrow = "→" if graph.is_directed() else "—"
    table = Table(show_header=True, header_style="bold", title="Edges")
    table.add_column("#", justify="right", style="dim")
    table.add_column("From", style="green")
    table.add_column("", justify="center")
    table.add_column("To", style="cyan")
    for i, e in enumerate(edges, 1):
        table.add_row(str(i), e.vertex1, arrow, e.vertex2)
    console.print(table)


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
    _kv("label", graph.get_label())
    _kv("vertices", graph.order())
    _kv("edges", graph.size())
    _kv("directed", graph.is_directed())

    console.print()
    _graph_panel(graph, "social network")

    # Other construction methods
    console.print()
    matrix = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    matrix_graph = Graph(input_matrix=matrix)
    _kv("from matrix", f"{matrix_graph.order()} vertices, {matrix_graph.size()} edges")

    manual = Graph("manual")
    for v in ("X", "Y", "Z"):
        manual.add_vertex(v)
    manual.add_edge("X", "Y")
    manual.add_edge("Y", "Z")
    _kv("programmatic", f"{manual.order()} vertices, {manual.size()} edges")

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
        nbrs = ", ".join(graph.get_neighbors(v)) or "(none)"
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

    :param graph: An undirected graph.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("6 · Complement graph")

    comp = get_complement(graph)
    _kv("original", f"{graph.order()} vertices, {graph.size()} edges")
    _kv("complement", f"{comp.order()} vertices, {comp.size()} edges")

    console.print()
    _edge_table(comp)


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

    matrix = graph.get_adjacency_matrix()
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

    console.print()
    console.rule("[bold green]Done![/bold green]")
    console.print(
        "  Explore the source at [link=https://github.com/nathan-gilbert/graphworks]"
        "src/graphworks/[/link]"
    )


if __name__ == "__main__":
    main()
