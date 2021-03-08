# Graphworks

## A Python module for efficient graph theoretic programming

**NOTE** This is a very old project I created for my undergrad capstone project.
It's not in a working state at the moment, but I'm bringing it back to life.

## Usage

TODO

## Development

### Requirements

- Python 3.7+
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

### Diagnostics

- Run the unit tests: `python -m unittest discover tests '*_tests.py'`
- Run unit test coverage: `coverage run --source=graphworks/ -m unittest discover tests '*_tests.py'`
- Generate test coverage reports (either works):
  - `coverage report --omit="*/test*,*/venv/*"`
  - `coverage html --omit="*/test*,*/venv/*"`

## TODO

- Make edges use the data class for all graph objects
- Allow for directed graphs
- <https://www.python-course.eu/graphs_python.php>
- Implement basic algorithms for directed graphs
  - Hierholzer’s Algorithm
  - <https://algs4.cs.princeton.edu/42digraph/>
- Allow for weighted graphs
  - Jarnik's algorithm
  - Dijkstra's algorithm
- <https://towardsdatascience.com/4-types-of-tree-traversal-algorithms-d56328450846>
- Create the documentation for usage
- C++ binaries for speeding up graph computations

