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

json_graph = {"label": "my graph", "edges": {"A": ["B"], "B": []}}
graph = Graph("my graph", input_graph=json.dumps(json_graph))
print(graph)
```

Optional extras:

```sh
pip install graphworks[matrix]   # numpy adjacency matrix support
pip install graphworks[viz]      # graphviz export
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
pre-commit run --all-files
```

### Publishing

Version is managed automatically via git tags using `hatchling-vcs`.

- Tag a commit: `git tag -a vX.Y.Z -m 'release message'`
- Push the tag: `git push --tags`
- The GitHub Actions workflow will build and publish to PyPI automatically.

## TODO

- Create Vertex class
- Build out directed graphs algorithms
  - <https://algs4.cs.princeton.edu/42digraph/>
- Allow for weighted graph algorithms
  - Jarnik's algorithm
  - Dijkstra's algorithm
- C++ binaries for speeding up graph computations
