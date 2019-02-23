
from numpy import *

class FunctionHandler:
    """A class to handle the various algorithms, the core graph-theoretic handler """

    def __init__(self, b, graph):
        """Receives buffer element so output can be redirected. """
        self.BUFFER = b
        self.GRAPH = graph

    def setGraph(self, graph):
        self.GRAPH = graph

    ###
    ### GRAPH THEORETIC ALGORITHMS
    ###
    def path(self, start, end, path=[]):
        """Finds and displays a path from start to end if one exists. Uses backtracking. """
        path = path + [start]

        if start == end:
            return path
        if start not in self.GRAPH.adj:
            return None
        for node in self.GRAPH.adj[start]:
            if node not in path:
                newpath = self.find_path(node, end, path)
                if newpath:
                    return newpath
        return None

    def find_path(self, node, end, path):
        return []

    def find_all_paths(self, start, end, path=[]):
        """Finds all paths. A generalization of the algorithm above."""
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.GRAPH.adj:
            return []
        paths = []
        for node in self.GRAPH.adj[start]:
            if node not in path:
                newpaths = self.find_all_paths(node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def cycle(self):
        """Checks for a cycle in a given graph. If it finds it, returns True, else False. This
        search can be exhaustive if looped over the keys in a keyList. """
        keyList = list(self.GRAPH.adj.keys())
        keyList.sort()
        s = keyList[0]
        keyList.remove(s)

        #0 = white
        #1 = grey
        color = {}
        pred = {}
        queue = []

        for vertex in keyList:
            self.GRAPH.color[vertex] = 0
            pred[vertex] = "$"	#$ = nil

        self.GRAPH.color[s] = 1
        pred[s] = "$"

        queue.insert(0, s)

        while len(queue) != 0:
            u = queue[0]

            for vertex in self.GRAPH.adj[u]:
                if self.GRAPH.color[vertex] == 0:
                    self.GRAPH.color[vertex] = 1
                    pred[vertex] = u
                    queue.insert(0,vertex)
                else:
                    if vertex == s and u != "$":
                        return True
            queue.pop()

        self.GRAPH.clearVisited()
        return False

    def connected(self):
        """Checks to see if a graph is connected."""

        conn = sum(self.GRAPH.matrix)

        for n in conn:
            if n == 0:
                return False

        return True

    def dom(self):
        """Returns a dominating set."""

        N = self.GRAPH.matrix + identity(self.GRAPH.matrix.shape[0])
        x = zeros((self.GRAPH.matrix.shape[0], 1))

        self.BUFFER.append(N)
        self.BUFFER.append(x)

        #When can we be sure that there is no larger sum??
        x_1 = sum(x)

    def sparse(self):
        """Checks how sparse or dense a graph is. |E| < |V^2| - 3."""

        #is 3 a good choice for approximately equal to?
        if self.GRAPH.edges < (self.GRAPH.vertices**2 - 3):
            self.BUFFER.append("Graph is sparse.")
        else:
            self.BUFFER.append("Graph is dense.")

    def BFS(self, s):
        """Implementation of Breadth First Search. """
        keyList = list(self.GRAPH.adj.keys())
        keyList.sort()
        keyList.remove(s)

        #0 = white
        #1 = grey
        #2 = black
        color = {}
        dist = {}
        pred = {}
        queue = []

        for vertex in keyList:
            self.GRAPH.color[vertex] = 0
            dist[vertex] = -1
            pred[vertex] = '$'	#$ = nil

        self.GRAPH.color[s] = 1
        dist[s] = 0
        pred[s] = '$'

        queue.insert(0, s)
        while len(queue) != 0:
            u = queue[0]
            for vertex in self.GRAPH.adj[u]:
                if self.GRAPH.color[vertex] == 0:
                    self.GRAPH.color[vertex] = 1
                    dist[vertex] = dist[u] + 1
                    pred[vertex] = u
                    queue.insert(0,vertex)
            queue.pop()
            self.GRAPH.color[u] = 2

        print(dist)
        self.GRAPH.clearVisited()

    def getUnvisited(self, v):
        """Returns any unvisited neighbors in a graph. """
        for n in self.GRAPH.adj[v]:
            if self.GRAPH.color[n] == 0:
                return n
            return "NIL"

    def DFS(self, start, goal):
        """Implementation of Depth First Search. """

        keyList = list(self.GRAPH.adj.keys())
        keyList.sort()
        stack = []
        color = {}

        for vertex in keyList:
            color[vertex] = 0

        self.GRAPH.color[start] = 1
        stack.insert(0, start)

        while len(stack) != 0:
            vertex = stack[0]
            if vertex == goal:
                print(stack)
                break
            else:
                neighbor = self.getUnvisited(vertex)
                if neighbor == "NIL":
                    del stack[0]
                else:
                    self.GRAPH.color[neighbor] = 1
                    stack.insert(0,neighbor)

            self.GRAPH.clearVisited()

