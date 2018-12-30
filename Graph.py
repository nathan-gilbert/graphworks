#!/usr/bin/python
#Nathan Gilbert
#graph.py implementation

from functions import *
from numpy import *
import copy

class Graph:
	def __init__(self, l):
		self.name = l													# A string representing the graphs name.
		self.adj = {}													# A dictionary where the keys are nodes and values are a Python list of neighbors.		
		self.matrix = zeros((3,3))									# A numpy adjacency matrix. 				
		self.edges = 0													# Number of edges.			
		self.vertices = 0												# Number of vertices.				
		self.adjl = False												# Used for initial read in purposes.
		self.matrixUpToDate = False   							# Are both representations up to date?			
		self.listUpToDate = False									# Are both representations up to date?			
		self.directed = False										# Does the graph have direction? Do I?
		self.weighted = False										# Do the edges have weights?
		self.color = {}												# Visited list.		

	def __repr__(self):
		return self.name

	def __str__(self):
		adjList = ''
		keyList = self.adj.keys()
		keyList.sort()
		for key in keyList:
			adjList += str(key) + " -> "
			for neighbor in self.adj[key]:
				adjList += " " + neighbor
			adjList += "\n"

		return "%s\n%s\n%s" % (self.name,adjList,self.matrix)

	def setName(self,s):
		self.name = s

	def makeGraphList(self, adjList):
		"""Creates and updates internal graph representations. """
		self.adj = adjList
		self.adjl = True
		self.matrixUpToDate = False
		self.update()

	def makeGraphMatrix(self,m):
		""" Creates and updates graph representations. """
		self.matrix = m
		self.listUpToDate = False
		self.update()

	def clearVisited(self):
		"""Clears the internal visited listed in a Graph. """
		for key in self.adj.keys():
			self.color[key] = 0

	def update(self):
		""" Switching from adjacentency list to matrix and vice versa. -1 means the vertices share no edge. """
		#in case any graph operations changes the number of vertices 
		#or edges. 
		self.vertices = 0
		self.edges = 0		

		#if list is upToDate then make the matrix
		if(self.adjl):
			row = 0
			keyList = self.adj.keys()
			keyList.sort()
			neighbor = []
			rank = len(keyList)

			#Creating a temp matrix for later use.
			tmpMatrix = zeros((rank,rank))
			
			for key in keyList:
				neighbor = self.adj[key]
				for n in neighbor:
					tmpMatrix[row,(ord(n) - 65)] = 1
				row += 1

			self.matrix = tmpMatrix
		
		#else make the list
		else:
			self.adj = {}
			neighbor = []
			index = -1 

			for n in range(self.matrix.shape[0]):
				for q in self.matrix[n,:]:
					index += 1
					if int(str(q)) > 0:
						neighbor.append(chr(index + 65))

				self.adj[chr(n + 65)] = copy.deepcopy(neighbor)		
				neighbor = []
				index = -1 
			
		#Setting number of edges & vertices in graph.
		self.edges = self.matrix.shape[0]
		
		for key in self.adj.keys():
			self.color[key] = 0
			self.vertices += len(self.adj[key])


#Below is for testing purposes. 
if __name__ == '__main__':
	
	g = Graph("g")
	inFile = open("./adjmatrix3w.txt", "r")
	row = []
	name = ''

	for line in inFile:
		if(line[0] == "#"):
			continue

		if line.find("Name:") != -1:
			name = line[5:]
			g.setName(name)
			continue

		if line == "\n":
			continue

		if line.find("+DIRECTED") != -1:
			g.directed = True
			continue
	
		if line.find("+WEIGHTED") != -1:
			g.weighted = True
			continue
			
		row.append(line.split())

	matrix = array(row)
	g.makeGraphMatrix(matrix)

	inFile.close()

	print g

	f = FunctionHandler("",g)

	search = raw_input("What do you want to start search from: ")

	f.BFS(search)
	
	start = raw_input("What do you want to start search from: ")
	end = raw_input("What do you want to search for: ")
	
	f.DFS(start,end)

	if(f.cycle('A')):
		print "Has cycle(s)"
	else:
		print "No cycles."

