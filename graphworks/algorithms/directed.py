
from graphworks.graph import Graph


def is_dag(graph: Graph) -> bool:
    """

    :param graph:
    :return: True/False if graph is a directed, acyclic graph
    """
    if not graph.is_directed():
        return False
    # TODO: finish DAG detection algorithm
    return False
