import json
from typing import List
from typing import DefaultDict
import uuid

import numpy as np
from numpy import ndarray
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Edge:
    terminus: str
    weight: float = None

    def has_weight(self) -> bool:
        if self.weight is None:
            return False
        return True

    def __repr__(self):
        return self.terminus


class Graph:
    """ The graph implementation as a simple adjacency map. """

    def __init__(self,
                 label: str = None,
                 input_file: str = None,
                 input_graph: str = None,
                 input_array: ndarray = None):
        """

        :param label: a name for this graph
        :param input_file: the absolute path to a json file containing a graph
        :param input_graph: a string containing json representing the graph
        """
        self.__label = label if label is not None else None
        self.__is_directed = False
        self.__graph = defaultdict(list)

        # process a file, string representing the graph or an ndarray
        # representation
        if input_file is not None:
            with open(input_file, 'r') as in_file:
                lines = ''.join(in_file.readlines())
                json_data = json.loads(lines)
                self.__extract_fields_from_json(json_data)
        elif input_file is None and input_graph is not None:
            json_data = json.loads(input_graph)
            self.__extract_fields_from_json(json_data)
        elif input_array is not None:
            if not self.__validate_array(input_array):
                raise ValueError("input array is malformed")
            self.__array_to_graph(input_array)

        if not self.__validate():
            raise ValueError("Edges don't match vertices")

    def vertices(self) -> List[str]:
        """ returns the vertices of a graph """
        return list(self.__graph.keys())

    def edges(self) -> List[set]:
        """ returns the edges of a graph """
        return self.__generate_edges()

    def get_graph(self) -> DefaultDict[str, List]:
        return self.__graph

    def get_label(self) -> str:
        return self.__label

    def is_directed(self) -> bool:
        return self.__is_directed

    def add_vertex(self, vertex: str):
        """ If the vertex "vertex" is not in
            self.__graph, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        if vertex not in self.__graph:
            self.__graph[vertex] = []

    def add_edge(self, edge: List):
        edge = set(edge)
        (vertex1, vertex2) = tuple(edge)
        if vertex1 in self.__graph:
            self.__graph[vertex1].append(vertex2)
        else:
            self.__graph[vertex1] = [vertex2]

        if vertex2 not in self.__graph:
            self.__graph[vertex2] = []

    def order(self) -> int:
        return len(self.vertices())

    def size(self) -> int:
        return len(self.edges())

    def get_adjacency_matrix(self) -> ndarray:
        shape = (self.order(), self.order())
        matrix = np.zeros(shape, dtype=int)
        for v in self.vertices():
            i = self.vertices().index(v)
            for edge in self.__graph[v]:
                j = self.vertices().index(edge)
                matrix[i][j] = 1
        return matrix

    @staticmethod
    def __validate_array(arr: ndarray) -> bool:
        if len(arr.shape) != 2:
            return False
        if arr.shape[0] != arr.shape[1]:
            return False
        return True

    def __repr__(self):
        return self.__label

    def __str__(self):
        """

        :return: a string rep of the graph with name and edges
        """
        final_string = ''
        key_list = list(self.__graph.keys())
        key_list.sort()
        for key in key_list:
            final_string += str(key) + " -> "
            if self.__graph[key]:
                for neighbor in self.__graph[key]:
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
                if self._index < len(self._graph.vertices()):
                    key = list(self._graph.vertices())[self._index]
                    self._index += 1
                    return key
                raise StopIteration

        return GraphIterator(self)

    def __getitem__(self, node):
        return self.__graph.get(node, [])

    def __extract_fields_from_json(self, json_data: dict):
        self.__label = json_data.get("label", "")
        self.__is_directed = json_data.get("directed", False)
        self.__is_weighted = json_data.get("weighted", False)
        self.__graph = json_data.get("graph", {})

    def __generate_edges(self) -> List[set]:
        """
            Generating the edges of the graph "graph". Edges are represented as
            sets with one (a loop back to the vertex) or two vertices
        """
        edges = []
        for vertex in self.__graph:
            for neighbour in self.__graph[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def __validate(self) -> bool:
        """
        Test to make sure that all edge endpoints are contained in the vertex
        list.
        :return: True if the vertex list matches all the edge endpoints
        """
        for vertex in self.__graph:
            for neighbor in self.__graph[vertex]:
                if neighbor not in self.__graph:
                    return False
        return True

    def __array_to_graph(self, arr: ndarray):
        names = [str(uuid.uuid4()) for _ in range(arr.shape[0])]
        for r_idx in range(arr.shape[0]):
            vertex = names[r_idx]
            for idx, val in enumerate(arr[r_idx]):
                if val > 0:
                    edge = names[idx]
                    self.__graph[vertex].append(edge)
