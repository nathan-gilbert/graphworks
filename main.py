import json
from graphworks.graph import Graph

if __name__ == "__main__":
    json_graph = {"name": "my graph", "edges": {"A": "B", "B": None}}
    g = Graph("my graph", input_str=json.dumps(json_graph))
    print(g)
