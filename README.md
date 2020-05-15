# Graphworks

## A Python module for efficient graph theoretic programming

This is a very old project I created for my undergrad capstone project. 
It's not in a working state at the moment but I'm bringing it back to life.

## Requirements

* Python 3.7+
* virtualenv
* numpy
* graphviz

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

## Usage

Run the unit tests: `python -m unittest discover tests '*_tests.py'`

Run unit test coverage: `coverage run --source=graphworks/ -m unittest discover tests '*_tests.py'`

Generate test coverage reports (either works): 

* `coverage report --omit="*/test*"` 
* `coverage html --omit="*/test*"` 

Using the library: TODO

## TODO

1. Start with a simple map representation of a graph
2. Implement the basic graph algorithms on this representation
