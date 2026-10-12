# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## Project Overview

Graphworks is a zero-dependency Python library for graph theory computation. It provides a `Graph`
class (with immutable `Vertex` and `Edge` value objects) and pure-function algorithm and export
modules for traversal, path-finding, properties, directed graph operations, and rendering. Optional
extras add numpy matrix interop (`[matrix]`) and Graphviz export (`[viz]`).

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

# Run all pre-commit hooks (CI also lints with ruff --preview rules such as PLR0917)
prek run --all-files
```

## Architecture

### Source layout: `src/graphworks/`

- **`graph.py`** — Core `Graph` class. Stores `_vertices: dict[str, Vertex]` and
  `_adj: dict[str, dict[str, Edge]]`. Undirected edges are stored under **both** endpoints (the
  same `Edge` object), so `neighbors()` is symmetric and `edges()` de-duplicates. Accepts JSON
  files/strings (neighbors may be bare names or `{"target", "weight", "label", "attrs"}` objects;
  optional `"vertices"` key for vertex labels/attrs) or stdlib adjacency matrices. Supports
  directed, weighted, and labeled graphs, fluent `add_*` chaining, `|`/`|=` union, and structural
  `==`.
- **`vertex.py`** / **`edge.py`** — Frozen `Vertex` and `Edge` dataclasses; identity is the name
  (vertex) or `(source, target, directed)` (edge). `Edge.create` / `Vertex.create` accept a plain
  `attrs` dict.
- **`types.py`** — Type alias `AdjacencyMatrix = list[list[int]]` (pure Python, no numpy).
- **`numpy_compat.py`** — Optional `ndarray_to_matrix` / `matrix_to_ndarray`, gated behind
  `[matrix]`. `Graph` does not take ndarrays directly; convert first.
- **`utilities.py`** — Private helpers shared across modules (`_freeze_attrs`, `_file_stem`).
- **`algorithms/`** — Pure functions that take a `Graph` as input:
   - `properties.py` — Degrees, connectivity, density, diameter, `complement`, etc.
   - `paths.py` — `find_path()`, `find_all_paths()`, `find_isolated_vertices()`
   - `search.py` — `breadth_first_search()`, `depth_first_search()`
   - `directed.py` — `is_dag()`, `find_circuit()` (Hierholzer's)
   - `sort.py` — `topological_sort()`
- **`export/`** — `save_to_json()`, `save_to_dot()` (needs `[viz]`), `to_text()`, `to_ascii()`.
  `_labels.py` holds the label/weight formatting shared by the renderers and DOT export.

### API conventions

- Unknown vertex names raise `KeyError`; `graph.vertex()` / `graph.edge()` return `None`.
- Predicates are vacuously true on an empty graph; undefined metrics raise `ValueError`.
- Failed preconditions raise `ValueError` (cyclic `topological_sort`, non-Eulerian
  `find_circuit`, disconnected `diameter`, directed/undirected `Edge` mismatch in `add_edge`).
- Degree = number of incident edges (in + out for directed; self-loop counts 2).
- Recursion/accumulator state stays in private helpers, never in public signatures.

### Tests: `tests/`

Tests mirror the source modules (e.g., `tests/algorithms/test_properties.py` tests
`algorithms/properties.py`). Shared JSON fixtures live in `conftest.py`; file fixtures (g1–g4) live
in `tests/data/`. Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`.

## Code Style and Conventions

- **Python 3.13+** required; `from __future__ import annotations` used throughout
- **PEP 257** docstrings on all public APIs; ruff enforces `ANN` (annotations) and `D` (docstrings)
  rules on `src/` but exempts `tests/`
- **Formatting:** black and ruff (line-length 100), isort (black profile)
- **Type checking:** ty in strict mode
- All algorithm functions are pure functions — no classes wrapping algorithms
- Version is dynamic via `hatchling-vcs` (git tags like `X.Y.Z`, no `v` prefix)

## Publishing

Tag a commit with `git tag -a X.Y.Z -m 'message'` and push tags to trigger PyPI publish via GitHub
Actions.
