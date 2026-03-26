# Graphworks

[![Python package](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml/badge.svg)](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml)

## A Python module for efficient graph theoretic programming

[Documentation](https://graphworks.readthedocs.io) |
[Wiki](https://github.com/nathan-gilbert/graphworks/wiki)

### Quick Start

```sh
pip install graphworks
```

```python
import json
from graphworks.graph import Graph

json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
graph = Graph(input_graph=json.dumps(json_graph))
print(graph)
```

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

- Tag a commit: `git tag -a vX.Y.Z -m 'release message'`
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
- [x] Edge weights, labels, and attributes survive all operations
- [x] `add_edge` supports `weight` and `label` keyword arguments
- [x] `edge()` lookup method for direct O(1) edge retrieval

### Tier 3: Lossless conversions

- [ ] `to_adjacency_matrix()` / `from_adjacency_matrix()` round-trips that preserve vertex names
      via an index mapping
- [ ] Fix `get_complement` to preserve original vertex names instead of generating UUIDs
- [ ] `to_edge_list()` / `from_edge_list()` conversions
- [ ] Parse weighted JSON format (e.g. `g4.json` dict-as-neighbor style)

### Tier 4: Algorithms

- [ ] Dijkstra's shortest path (weighted)
- [ ] Prim's / Kruskal's minimum spanning tree
- [ ] Strongly connected components (Tarjan or Kosaraju)
- [ ] Improved shortest-path implementations leveraging weighted edges

### Tier 5: Export and CLI

- [x] JSON export (`save_to_json`)
- [x] Graphviz DOT export (`save_to_dot`)
- [x] Rich-based demo script (`uv run demo`)
- [ ] CLI application for common graph operations
- [ ] Rich rendering integration for interactive graph display

### Tier 6: Cross-cutting quality

- [ ] Thread safety (immutable graph views or locking around mutations)
- [ ] Input validation hardening
- [ ] Performance benchmarks
