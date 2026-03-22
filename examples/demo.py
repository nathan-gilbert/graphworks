#!/usr/bin/env python3
"""Graphworks demo — a quick tour of the library's core features.

Run with::

    uv run demo

Or directly::

    uv run python examples/demo.py

This script is **not** shipped with the library.  It lives in the ``examples/``
directory and is registered as a ``[project.scripts]`` entry point for
convenience during development.
"""

from __future__ import annotations

import json

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
)
from graphworks.graph import Graph


def _section(title: str) -> None:
    """Print a section header to stdout.

    :param title: Section heading text.
    :type title: str
    :return: Nothing.
    :rtype: None
    """
    width = 60
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


def demo_construction() -> Graph:
    """Demonstrate the three ways to construct a Graph.

    :return: The JSON-constructed graph used in subsequent demos.
    :rtype: Graph
    """
    _section("1 · Graph construction")

    # --- From a JSON string ---
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
    print(f"From JSON string  → {graph.order()} vertices, {graph.size()} edges")
    print(f"  label : {graph.get_label()}")
    print(f"  verts : {graph.vertices()}")

    # --- From an adjacency matrix ---
    matrix = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]
    matrix_graph = Graph(input_matrix=matrix)
    print(f"\nFrom matrix       → {matrix_graph.order()} vertices, {matrix_graph.size()} edges")

    # --- Programmatic construction ---
    manual = Graph("manual")
    for v in ("X", "Y", "Z"):
        manual.add_vertex(v)
    manual.add_edge("X", "Y")
    manual.add_edge("Y", "Z")
    print(f"Programmatic      → {manual.order()} vertices, {manual.size()} edges")

    return graph


def demo_properties(graph: Graph) -> None:
    """Show structural property queries.

    :param graph: An undirected graph to inspect.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("2 · Structural properties")

    print(f"  connected?   {is_connected(graph)}")
    print(f"  complete?    {is_complete(graph)}")
    print(f"  simple?      {is_simple(graph)}")
    print(f"  regular?     {is_regular(graph)}")
    print(f"  density      {density(graph):.4f}")
    print(f"  diameter     {diameter(graph)}")
    print(f"  deg sequence {degree_sequence(graph)}")

    isolated = find_isolated_vertices(graph)
    print(f"  isolated     {isolated if isolated else '(none)'}")


def demo_traversal(graph: Graph) -> None:
    """Run BFS and DFS from a starting vertex.

    :param graph: An undirected graph to traverse.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("3 · Traversals")

    start = graph.vertices()[0]
    bfs = breadth_first_search(graph, start)
    dfs = depth_first_search(graph, start)
    print(f"  BFS from {start!r}: {bfs}")
    print(f"  DFS from {start!r}: {dfs}")


def demo_paths(graph: Graph) -> None:
    """Demonstrate path-finding between two vertices.

    :param graph: An undirected graph to search.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("4 · Path finding")

    src, dst = "Alice", "Eve"
    single = find_path(graph, src, dst)
    print(f"  One path {src} → {dst}: {single}")

    all_paths = find_all_paths(graph, src, dst)
    print(f"  All paths ({len(all_paths)} total):")
    for p in all_paths:
        print(f"    {' → '.join(p)}")


def demo_complement(graph: Graph) -> None:
    """Show the complement graph.

    :param graph: An undirected graph.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("5 · Complement graph")

    comp = get_complement(graph)
    print(f"  Original : {graph.order()} vertices, {graph.size()} edges")
    print(f"  Complement: {comp.order()} vertices, {comp.size()} edges")


def demo_directed() -> None:
    """Demonstrate directed graph features: DAG detection and topological sort.

    :return: Nothing.
    :rtype: None
    """
    _section("6 · Directed graphs")

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
    print(f"  DAG?            {is_dag(dag)}")
    print(f"  Topo sort       {topological(dag)}")

    # Introduce a cycle: deploy → lint → … → deploy
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
    print(f"\n  Cyclic graph    DAG? {is_dag(cyclic)}")


def demo_iteration(graph: Graph) -> None:
    """Show iteration and subscript access on a graph.

    :param graph: An undirected graph.
    :type graph: Graph
    :return: Nothing.
    :rtype: None
    """
    _section("7 · Iteration & subscript access")

    for vertex in graph:
        neighbours = graph[vertex]
        print(f"  {vertex:>8} → {neighbours}")


def main() -> None:
    """Run all demo sections.

    :return: Nothing.
    :rtype: None
    """
    print("=" * 60)
    print("  graphworks — library demo")
    print("=" * 60)

    graph = demo_construction()
    demo_properties(graph)
    demo_traversal(graph)
    demo_paths(graph)
    demo_complement(graph)
    demo_directed()
    demo_iteration(graph)

    print(f"\n{'─' * 60}")
    print("  Done!  Explore the source at src/graphworks/")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    main()
