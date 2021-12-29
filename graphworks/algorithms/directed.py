from graphworks.graph import Graph
from graphworks.algorithms.search import arrival_departure_dfs


def is_dag(graph: Graph) -> bool:
    """

    :param graph:
    :return: True/False if graph is a directed, acyclic graph
    """
    if not graph.is_directed():
        return False

    departure = {v: 0 for v in graph.vertices()}
    discovered = {v: False for v in graph.vertices()}
    time = -1

    # not needed in this case
    arrival = {v: 0 for v in graph.vertices()}

    # visit all connected components of the graph, build departure dict
    for n in graph.vertices():
        if not discovered[n]:
            time = arrival_departure_dfs(graph, n, discovered, arrival, departure, time)

    # check if the given directed graph is DAG or not
    for n in graph.vertices():

        # check if (u, v) forms a back-edge.
        for v in graph.get_neighbors(n):
            # If the departure time of vertex `v` is greater than equal
            # to the departure time of `u`, they form a back edge.

            # `departure[u]` will be equal to `departure[v]` only if
            # `u = v`, i.e., a vertex with an edge to itself
            if departure[n] <= departure[v]:
                return False

    # No back edges
    return True
