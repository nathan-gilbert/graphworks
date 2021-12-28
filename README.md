# Graphworks

[![Python package](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package.yml/badge.svg)](https://github.com/nathan-gilbert/graphworks/actions/workflows/python-package.yml)

## A Python module for efficient graph theoretic programming

**NOTE** This is a very old project I created for my undergrad capstone project.
It's not in a working state at the moment, but I'm bringing it back to life.

## Usage

TODO

## Development

### Requirements

- Python 3.9+
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

- Run `python setup.py sdist bdist_wheel`
- Run `twine check dist/*`

### Diagnostics

- Run the unit tests: `python -m unittest discover tests '*_tests.py'`
- Run unit test coverage: `coverage run --source=graphworks/ -m unittest discover tests '*_tests.py'`
- Generate test coverage reports (either works):
  - `coverage report --omit="*/test*,*/venv/*"`
  - `coverage html --omit="*/test*,*/venv/*"`

## TODO

- Create the documentation for usage
- Searching/Sorting
  - Topological sort
  - <https://towardsdatascience.com/4-types-of-tree-traversal-algorithms-d56328450846>
- <https://www.python-course.eu/graphs_python.php>
- Build out directed graphs algorithms
  - Hierholzer’s Algorithm
  - <https://algs4.cs.princeton.edu/42digraph/>
- Allow for weighted graph algorithms
  - Jarnik's algorithm
  - Dijkstra's algorithm
- C++ binaries for speeding up graph computations

