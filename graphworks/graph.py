import copy

from numpy import array
from numpy import zeros

from graphworks.algorithms.dag import FunctionHandler


class Graph:
    """ The graph implementation """

    def __init__(self, label):
        # A string label for the graph
        self.name = label
        # A dictionary where the keys are nodes and values are a Python list of neighbors.
        self.adj = {}
        # A numpy adjacency matrix.
        self.matrix = zeros((3, 3))
        # Number of edges.
        self.edges = 0
        # Number of vertices.
        self.vertices = 0
        # Used for initial read in purposes.
        self.is_adjacency_list_representation = False
        # Are both representations up to date?
        self.is_matrix_up_to_date = False
        # Are both representations up to date?
        self.is_list_up_to_date = False
        # Does the graph have direction? Do I?
        self.is_directed = False
        # Do the edges have weights?
        self.is_weighted = False
        # Visited list.
        self.color = {}

    def __repr__(self):
        return self.name

    def __str__(self):
        adjacency_list = ''
        key_list = list(self.adj.keys())
        key_list.sort()
        for key in key_list:
            adjacency_list += str(key) + " -> "
            for neighbor in self.adj[key]:
                adjacency_list += " " + neighbor
            adjacency_list += "\n"

        return "%s\n%s\n%s" % (self.name, adjacency_list, self.matrix)

    def set_name(self, n):
        self.name = n

    def make_graph_list(self, adjacency_list):
        """Creates and updates internal graph representations. """
        self.adj = adjacency_list
        self.is_adjacency_list_representation = True
        self.is_matrix_up_to_date = False
        self.update()

    def make_graph_matrix(self, m):
        """ Creates and updates graph representations. """
        self.matrix = m
        self.is_list_up_to_date = False
        self.update()

    def clear_visited(self):
        """Clears the internal visited listed in a Graph. """
        for key in list(self.adj.keys()):
            self.color[key] = 0

    def update(self):
        """ Switching from adjacency list to matrix and vice versa. -1 means the vertices share no edge. """

        # in case any graph operations changes the number of vertices
        # or edges.
        self.vertices = 0
        self.edges = 0

        # if list is upToDate then make the matrix
        if self.is_adjacency_list_representation:
            key_list = list(self.adj.keys())
            key_list.sort()
            rank = len(key_list)

            # Creating a temp matrix for later use.
            tmp_matrix = zeros((rank, rank))

            current_row = 0
            for key in key_list:
                neighbor = self.adj[key]
                for n in neighbor:
                    tmp_matrix[current_row, (ord(n) - 65)] = 1
                current_row += 1

            self.matrix = tmp_matrix

        # else make the list
        else:
            self.adj = {}
            neighbor = []
            index = -1

            for n in range(self.matrix.shape[0]):
                for q in self.matrix[n, :]:
                    index += 1
                    if int(str(q)) > 0:
                        neighbor.append(chr(index + 65))

                self.adj[chr(n + 65)] = copy.deepcopy(neighbor)
                neighbor = []
                index = -1

        # Setting number of edges & vertices in graph.
        self.edges = self.matrix.shape[0]
        for key in list(self.adj.keys()):
            self.color[key] = 0
            self.vertices += len(self.adj[key])


# Below is for testing purposes.
if __name__ == '__main__':

    g = Graph("g")
    inFile = open("./adjmatrix3w.txt", "r")
    row = []
    name = ''

    for line in inFile:
        if line[0] == "#":
            continue

        if line.find("Name:") != -1:
            name = line[5:]
            g.set_name(name)
            continue

        if line == "\n":
            continue

        if line.find("+DIRECTED") != -1:
            g.is_directed = True
            continue

        if line.find("+WEIGHTED") != -1:
            g.is_weighted = True
            continue

        row.append(line.split())

    matrix = array(row)
    g.make_graph_matrix(matrix)

    inFile.close()

    print(g)

    f = FunctionHandler("", g)

    search = input("What do you want to start search from: ")

    f.BFS(search)

    start = input("What do you want to start search from: ")
    end = input("What do you want to search for: ")

    f.DFS(start, end)

    if f.cycle():
        print("Has cycle(s)")
    else:
        print("No cycles.")
