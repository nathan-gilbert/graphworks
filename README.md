# Graphworks Project

## A Python module for efficient graph theoretic processing

This is a very old project I created for a class as an Undergrad. It's not in a
working state at the moment but I'm getting back into the mathematics involved here
and am slowly reworking and improving the code quality.

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

## Notes

1. Currently, weighted graphs can only be entered using an adjacency matrix.

## TODO

1. Rework this a proper python module 
1. Remove the 'main.py' file, move some of that functionality down
