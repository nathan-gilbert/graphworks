# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Graphworks is a zero-dependency Python library for graph theory computation. It provides a `Graph` class using adjacency-list storage and pure-function algorithm modules for traversal, path-finding, properties, and directed graph operations. Optional extras add numpy matrix interop (`[matrix]`) and Graphviz export (`[viz]`).

## Development Commands

**Package manager:** uv (required >= 0.10.12)

```sh
# Install all dev dependencies
uv sync --extra all

# Run tests (includes coverage; fails under 90%)
uv run pytest

# Run a single test file
uv run pytest tests/test_graph.py

# Run a single test by name
uv run pytest tests/test_graph.py -k "test_method_name"

# Lint and format
uv run ruff check --fix src/ tests/
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run ty check

# Code complexity
uv run xenon --max-average=A --max-modules=B --max-absolute=B src/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Architecture

### Source layout: `src/graphworks/`

- **`graph.py`** — Core `Graph` class. Stores graphs as `defaultdict[str, list[str]]`. Accepts JSON files/strings, stdlib adjacency matrices, or numpy arrays as input. Supports directed, weighted, and labeled graphs.
- **`edge.py`** — `Edge` dataclass (`vertex1`, `vertex2`, `directed`, `weight`).
- **`types.py`** — Type alias `AdjacencyMatrix = list[list[int]]` (pure Python, no numpy).
- **`numpy_compat.py`** — Optional numpy interop, gated behind `[matrix]` extra.
- **`algorithms/`** — Pure functions that take a `Graph` as input:
  - `properties.py` — Degree, connectivity, density, complement, etc.
  - `paths.py` — `find_path()`, `find_all_paths()`, `find_isolated_vertices()`
  - `search.py` — BFS, DFS, arrival/departure DFS
  - `directed.py` — `is_dag()`, `find_circuit()` (Hierholzer's), `build_neighbor_matrix()`
  - `sort.py` — Topological sort
- **`export/`** — `save_to_json()` and `save_to_dot()` standalone functions.
- **`data/`** — JSON test graph fixtures (g1–g4).

### Tests: `tests/`

Tests mirror the source modules (e.g., `test_properties.py` tests `algorithms/properties.py`). Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`.

## Code Style and Conventions

- **Python 3.13+** required; `from __future__ import annotations` used throughout
- **PEP 257** docstrings on all public APIs; ruff enforces `ANN` (annotations) and `D` (docstrings) rules on `src/` but exempts `tests/`
- **Formatting:** black (line-length 88), isort (black profile)
- **Type checking:** ty in strict mode
- All algorithm functions are pure functions — no classes wrapping algorithms
- Version is dynamic via `hatchling-vcs` (git tags like `vX.Y.Z`)

## Publishing

Tag a commit with `git tag -a vX.Y.Z -m 'message'` and push tags to trigger PyPI publish via GitHub Actions.
