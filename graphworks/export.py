#!/usr/bin/python
#Export module for grapfwerk.
#
#Exports current graph to a graphviz file.
#use the program dot

from time import gmtime, strftime
from copy import deepcopy

class ExportHandler:

	def __init__(self,g):
		self.graph = g
		curTime = strftime("%m-%d-%Y-%H:%M:%S-0500", gmtime())
		self.fileName = self.graph.name.strip().replace(" ","") + ":" + curTime.strip() + ".dot"

	def makeGraphviz(self):
		self.outFile = open(self.fileName, "w")

		header = "digraph " + self.graph.name.strip().replace(" ","") + " {\nnode[shape=circle,width=0.2,height=0.2]\nedge[dir=none]\n"
		
		theMagic = ""
		keyList = self.graph.adj.keys()
		keyList.sort()

		#Graphviz needs a file that looks something like a directed graph, even though it isn't per se.
		#Removing such pecularities. 
		newDict = deepcopy(self.graph.adj)

		for key in keyList:
			for vert in newDict[key]:
				if key in newDict[vert]:
					newDict[vert].remove(key)

		#Actually generating the Graphviz.
		for key in keyList:
			newDict[key].sort()
			for node in newDict[key]:
				theMagic += "\"" + key + "\"" + " -> \"" + node + "\";\n"

		footer = "\n} "	

		self.outFile.write(header + theMagic + footer)

	def saveGraph(self):
		"""This function saves the current graph into a *.gwk file.  """

		name = self.graph.name
		buf = ""

		outFile = open(name.strip() + ".gwk", "w")
		outFile.write("Name: " + name.strip() + "\n")
	
		for key in self.graph.adj:
			buf = key + " -> "
			for n in self.graph.adj[key]:
				buf += " %s " % n
			buf += "\n"
			outFile.write(buf)
			buf = ""

	def getFileName(self):
		return self.fileName
		
	def __del__(self):
		self.outFile.close()

