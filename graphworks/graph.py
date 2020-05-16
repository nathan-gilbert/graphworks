import json


class Graph:
    """ The graph implementation as a simple adjacency map"""

    def __init__(self, label=None, input_file=None, input_str=None):
        self.__label = label if label is not None else None
        self.edges = {}

        # process either a file or string representing the graph
        if input_file is not None:
            with open(input_file, 'r') as inFile:
                lines = ''.join(inFile.readlines())
                json_data = json.loads(lines)
                self.__label = json_data.get("name", "")
                self.edges = json_data.get("edges", {})

        if input_file is None and input_str is not None:
            json_data = json.loads(input_str)
            self.__label = json_data.get("name", "")
            self.edges = json_data.get("edges", {})

    def __repr__(self):
        return self.__label

    def __str__(self):
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

    def get_label(self):
        return self.__label


