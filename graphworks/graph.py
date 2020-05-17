import json


class Graph:
    """ The graph implementation as a simple adjacency map"""

    def __init__(self,
                 label: str = None,
                 input_file: str = None,
                 input_graph: str = None):
        """

        :param label: a name for this graph
        :param input_file: the absolute path to a json file containing a graph
        :param input_graph: a string containing json representing the graph
        """
        self.__label = label if label is not None else None
        self.__is_directed = False
        self.edges = {}

        # process either a file or string representing the graph
        if input_file is not None:
            with open(input_file, 'r') as in_file:
                lines = ''.join(in_file.readlines())
                json_data = json.loads(lines)
                self._extract_fields_from_json(json_data)
        elif input_file is None and input_graph is not None:
            json_data = json.loads(input_graph)
            self._extract_fields_from_json(json_data)

    def __repr__(self):
        return self.__label

    def __str__(self):
        """

        :return: a string rep of the graph with name and edges
        """
        final_string = ''
        key_list = list(self.edges.keys())
        key_list.sort()
        for key in key_list:
            final_string += str(key) + " -> "
            if self.edges[key]:
                for neighbor in self.edges[key]:
                    final_string += neighbor
            else:
                final_string += "0"
            final_string += "\n"
        final_string = final_string.strip()
        return f"{self.__label}\n{final_string}"

    def __iter__(self):
        # pylint: disable=too-few-public-methods
        class GraphIterator:
            """
            Iterator class for Graphs
            """
            def __init__(self, g: Graph):
                self._graph = g
                self._index = 0

            def __next__(self):
                if self._index < len(self._graph.edges.keys()):
                    key = list(self._graph.edges.keys())[self._index]
                    self._index += 1
                    return key
                raise StopIteration
        return GraphIterator(self)

    def __getitem__(self, node):
        return self.edges.get(node, [])

    def get_label(self) -> str:
        return self.__label

    def is_directed(self) -> bool:
        return self.__is_directed

    def _extract_fields_from_json(self, json_data: dict):
        self.__label = json_data.get("label", "")
        self.__is_directed = json_data.get("directed", False)
        self.edges = json_data.get("edges", {})
