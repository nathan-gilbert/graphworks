# Graphworks

[![Python package](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml/badge.svg)][1]

## A Python module for efficient graph theoretic programming

[Wiki](https://github.com/nathan-gilbert/graphworks/wiki)

### Quick Start

```sh
pip install graphworks
```

```python
from graphworks import Graph, to_text
from graphworks.algorithms import find_path, is_connected

graph = Graph("roads").add_edge("A", "B", weight=2).add_edge("B", "C", label="toll")
print(graph.neighbors("B"))        # ['A', 'C'] — undirected edges work both ways
print(find_path(graph, "C", "A"))  # ['C', 'B', 'A']
print(is_connected(graph))         # True
print(to_text(graph))
```

Graphs can also be loaded from JSON (`Graph(input_file=...)` / `Graph(input_graph=...)`); a
neighbor may be a bare name or an object carrying edge data:

```json
{
  "label": "roads",
  "directed": false,
  "weighted": true,
  "vertices": { "A": { "label": "Alpha" } },
  "graph": { "A": ["B", { "target": "C", "weight": 2.5, "label": "toll" }], "B": [], "C": [] }
}
```

`save_to_json` writes this same format, so weights, labels, and attributes round-trip.

### API conventions

- `Graph` is the only class; algorithms (`graphworks.algorithms`) and exporters
  (`graphworks.export`) are free functions that take a `Graph`.
- A vertex name that is not in the graph raises `KeyError` (`graph[v]`, `neighbors`, and every
  algorithm). The `dict.get`-style `graph.vertex(name)` and `graph.edge(u, v)` return `None`.
- Predicates are vacuously true on an empty graph; metrics that are undefined there
  (`min_degree`, `max_degree`, `diameter`) raise `ValueError`.
- Algorithms whose precondition fails raise `ValueError` rather than returning a wrong answer
  (`topological_sort` on a cyclic graph, `find_circuit` on a non-Eulerian graph, `diameter` on a
  disconnected graph).
- Degree counts every incident edge (in + out for directed graphs; a self-loop counts twice).

Optional extras:

```sh
pip install graphworks[matrix]   # numpy adjacency matrix support
pip install graphworks[viz]      # graphviz export
pip install graphworks[docs]     # generate documentation
```

## Development

### Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (>= 0.10.12)

### Setup

```sh
uv sync --extra all
```

### Running Tests

```sh
# Run all tests (includes coverage; fails under 90%)
uv run pytest

# Run a single test file
uv run pytest tests/test_graph.py

# Run a single test by name
uv run pytest tests/test_graph.py -k "test_method_name"
```

### Linting and Formatting

```sh
# Lint
uv run ruff check --fix src/ tests/

# Format
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run ty check

# Code complexity
uv run xenon --max-average=A --max-modules=B --max-absolute=B src/

# Run all pre-commit hooks
prek run --all-files
```

### Publishing

Version is managed automatically via git tags using `hatchling-vcs`.

- Tag a commit: `git tag -a X.Y.Z -m 'release message'`
- Push the tag: `git push --tags`
- The GitHub Actions workflow will build and publish to PyPI automatically.

## Roadmap

### Tier 1: Data model

- [x] `Vertex` class with name, optional label, and immutable attribute mapping
- [x] `Edge` dataclass with source, target, directed flag, optional weight, label, and attributes
- [x] Both classes are frozen (immutable) with identity-based equality and hashing

### Tier 2: Graph refactor

- [x] Internal storage uses `dict[str, Vertex]` for vertex lookup
- [x] Adjacency structure uses `dict[str, dict[str, Edge]]` for O(1) edge access
- [x] Edge weights, labels, and attributes survive union, complement (vertices), and JSON/DOT
      export
- [x] `add_edge` supports `weight` and `label` keyword arguments
- [x] `edge()` lookup method for direct O(1) edge retrieval
- [x] `remove_vertex()` / `remove_edge()` (chainable; removing a vertex drops its incident edges)
- [x] `copy()` (independent structure, shared immutable `Vertex`/`Edge` objects)
- [x] `predecessors()` for directed graphs (O(V); same as `neighbors()` when undirected)

### Tier 3: Lossless conversions

- [ ] `to_adjacency_matrix()` / `from_adjacency_matrix()` round-trips that preserve vertex names
      via an index mapping
- [x] `complement` preserves original vertex names and the `directed` flag
- [ ] `to_edge_list()` / `from_edge_list()` conversions
- [x] Weighted JSON format (`{"target": ..., "weight": ...}` neighbor objects, see `g4.json`)

### Tier 4: Algorithms

- [ ] Unweighted shortest path via BFS (`find_path` returns *a* path, not the shortest;
      `diameter` already computes BFS distances internally)
- [ ] Dijkstra's shortest path (weighted)
- [ ] Prim's / Kruskal's minimum spanning tree
- [ ] Strongly connected components (Tarjan or Kosaraju) and `is_strongly_connected`

### Tier 5: Export and CLI

- [x] JSON export (`save_to_json`, lossless round-trip)
- [x] Graphviz DOT export (`save_to_dot`, with vertex/edge labels and weights)
- [x] Text tree and 2-D ASCII rendering (`to_text`, `to_ascii`)
- [x] Rich-based demo script (`uv run demo`)
- [ ] CLI application for common graph operations
- [ ] Rich rendering integration for interactive graph display

### Tier 6: Cross-cutting quality

- [ ] Iterative traversals: `find_path`, `find_all_paths`, and `topological_sort` are recursive and
      raise `RecursionError` on a ~3,000-vertex chain
- [ ] Input validation hardening:
   - [ ] Reject non-list neighbor values in JSON (`{"A": "B"}` is silently read as the characters
         of `"B"`)
   - [ ] Raise when more than one of `input_file` / `input_graph` / `input_matrix` is given (extras
         are silently ignored)
- [ ] Read-only graph view (instead of locking for thread safety)
- [ ] Performance benchmarks
- [ ] Run docstring examples as tests (`--doctest-modules`) so examples cannot go stale

### Tier 7: Docs and releases

- [ ] `CHANGELOG.md` (linked from the PyPI metadata but missing), starting with the 0.10.0
      breaking changes
- [ ] Hosted API documentation (Sphinx deps exist in the `[docs]` extra, but there is no `docs/`
      source and the Read the Docs site does not exist)

[1]: https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml
