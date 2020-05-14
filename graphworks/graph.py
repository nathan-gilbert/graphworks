import json


class Graph:
    """ The graph implementation as a simple adjacency map"""

    def __init__(self, label, input_file=None, input_str=None):
        # A string label for the graph
        self.name = label
        # A dictionary where the keys are nodes and values are a Python list of neighbors.
        self.edges = {}

        # h
        if input_file is not None:
            with open(input_file, 'r') as inFile:
                lines = ''.join(inFile.readlines())
                json_data = json.loads(lines)
                self.name = json_data.get("name", "")
                self.edges = json_data.get("edges", {})
        if input_file is None and input_str is not None:
            json_data = json.loads(input_str)
            self.name = json_data.get("name", "")
            self.edges = json_data.get("edges", {})

    def __repr__(self):
        return self.name

    def __str__(self):
        adjacency_list = ''
        key_list = list(self.edges.keys())
        key_list.sort()
        for key in key_list:
            adjacency_list += str(key) + " -> "
            for neighbor in self.edges[key]:
                adjacency_list += " " + neighbor
            adjacency_list += "\n"

        return f"${self.name}\n${adjacency_list}"
