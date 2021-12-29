import json
import unittest

from graphworks.algorithms.search import breadth_first_search
from graphworks.algorithms.search import depth_first_search
from graphworks.algorithms.search import arrival_departure_dfs
from graphworks.graph import Graph


class SearchTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simple_graph = {"graph": {
            "a": ["b", "c"],
            "b": ["c"],
            "c": ["a", "d"],
            "d": ["d"]
        }}

    def test_breadth_first_search(self):
        graph = Graph(input_graph=json.dumps(self.simple_graph))
        walk = breadth_first_search(graph, "c")
        self.assertListEqual(["c", "a", "d", "b"], walk)

    def test_depth_first_search(self):
        graph = Graph(input_graph=json.dumps(self.simple_graph))
        walk = depth_first_search(graph, "c")
        self.assertListEqual(["c", "d", "a", "b"], walk)

    def test_arrival_departure_dfs(self):
        disjoint_graph = {"graph": {
            "a": ["b", "c"],
            "b": [],
            "c": ["d", "e"],
            "d": ["b", "f"],
            "e": ["f"],
            "f": [],
            "g": ["h"],
            "h": []
        }, "directed": True}

        graph = Graph(input_graph=json.dumps(disjoint_graph))

        # list to store the arrival time of vertex
        arrival = {v: 0 for v in graph.vertices()}
        # list to store the departure time of vertex
        departure = {v: 0 for v in graph.vertices()}
        # mark all the vertices as not discovered
        discovered = {v: False for v in graph.vertices()}
        time = -1

        for v in graph.vertices():
            if not discovered[v]:
                time = arrival_departure_dfs(graph, v, discovered, arrival, departure, time)

        # pair up the arrival and departure times and ensure correct ordering
        result = list(zip(arrival.values(), departure.values()))
        expected_times = [(0, 11), (1, 2), (3, 10), (4, 7), (8, 9), (5, 6), (12, 15), (13, 14)]
        self.assertListEqual(expected_times, result)


if __name__ == '__main__':
    unittest.main()
