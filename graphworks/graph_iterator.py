class GraphIterator:
    """
    Iterator class for Graphs
    """
    def __init__(self, g):
        self._graph = g
        self._index = 0

    def __next__(self):
        if self._index < len(self._graph.edges.keys()):
            key = list(self._graph.edges.keys())[self._index]
            edges = self._graph.edges[key]
            self._index += 1
            return edges
        raise StopIteration
