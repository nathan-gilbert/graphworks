# Graphworks

[![Python package](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml/badge.svg)](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package-ci.yml)

## A Python module for efficient graph theoretic programming

## Usage

See the [wiki](https://github.com/nathan-gilbert/graphworks/wiki)

### TLDR

First, `pip install graphworks`

```python
import json
from src.graphworks.graph import Graph

json_graph = {"label": "my graph", "edges": {"A": ["B"], "B": []}}
graph = Graph("my graph", input_graph=json.dumps(json_graph))
print(graph)
```

## Development

### Requirements

- Python 3.8+
- virtualenv
- numpy
- graphviz

### Install the required packages

```sh
pip install virtualenv
virtualenv env
```

### Start the virtualenv

```sh
source ./env/bin/activate
```

### You can deactivate the virtualenv with

```sh
deactivate
```

### Lastly, install the required libraries

```sh
pip install -r requirements.txt
```

### Building the package

- Update the version number in `graphworks.__init__.py`
- Run `python -m build`
- Run `twine check dist/*`
- Upload to test PyPi: `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
- Upload to PyPi main: `twine upload --skip-existing dist/*`
- To autopublish, tag commit with `git tag -a vX.Y.Z -m 'release message`
- Then `git push --tags`

### Diagnostics

- Run the unit tests: `python -m unittest discover tests '*_tests.py'`
- Run unit test coverage: `coverage run --source=graphworks/ -m unittest discover tests '*_tests.py'`
- Generate test coverage reports (either works):
  - `coverage report --omit="*/test*,*/venv/*"`
  - `coverage html --omit="*/test*,*/venv/*"`

## TODO

- Create Vertex class
- <https://www.python-course.eu/graphs_python.php>
- Build out directed graphs algorithms
  - <https://algs4.cs.princeton.edu/42digraph/>
- Allow for weighted graph algorithms
  - Jarnik's algorithm
  - Dijkstra's algorithm
- C++ binaries for speeding up graph computations
