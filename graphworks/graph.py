import json


class Graph:
    """ The graph implementation as a simple adjacency map"""

    def __init__(self, label, input_file=None, input_str=None):
        self.name = label
        self.edges = {}

        # process either a file or string representing the graph
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
            if self.edges[key] is not None:
                for neighbor in self.edges[key]:
                    adjacency_list += neighbor
            else:
                adjacency_list += "0"
            adjacency_list += "\n"

        return f"{self.name}\n{adjacency_list}"


if __name__ == "__main__":
    json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
    g = Graph("my graph", input_str=json.dumps(json_graph))
    print(g)
