import os
import sys
from copy import deepcopy
from random import randrange
from time import asctime
import numpy
import graphworks
from graphworks import export
from graphworks.graph import Graph
from graphworks.algorithms.dag import FunctionHandler


def main(argv):
    """Where the magic happens.  """

    #general config options.
    haveFile = False
    adjList = False
    gui = False

    #locals
    inFile = " "

    # TODO convert to argparse
    if "--debug" in argv:
        DEBUG = True
        try:
            currTime = asctime().split()[3]
            debugLog = open("#graphworks:%s.debug" % currTime, "w")
            debugLog.write("Debug Log for %s" % currTime)
        except ValueError:
            print("Error opening debug file.")
            sys.exit(1)

    if "-h" in argv or "--help" in argv:
        print("""\n\tGrapfworks 0.3\n\tA Graph Theoretic black hole.""")
        print("""
              -al <file> or --adjacency-list <file>        - <file> is given in adjacency list format.
              -am <file> or --adjacency-matrix <file>      - <file> is given in adjacency matrix format.
              -x <file>                                    - <file> is exported as a Graphviz file.
              --gui                                        - Grapfwerks GUI.
              """)
        print("""\tAuthor: Nathan Gilbert (nathan.gilbert@gmail.com) """)
        sys.exit(0)

    #The next two arguments determine the input type of the graph.
    if "-al" in argv or "--adjaceny-list" in argv:
        try:
            inFile = argv[argv.index("-al") + 1]
            haveFile = True
            adjList = True
        except ValueError:
            try:
                inFile = argv[argv.index("--adjaceny-list") + 1]
                haveFile = True
            except:
                print("Command line arguments incorrect. 1")

    if "-am" in argv or "--adjaceny-matrix" in argv:
        try:
            inFile = argv[argv.index("-am") + 1]
            haveFile = True
        except ValueError:
            try:
                inFile = argv[argv.index("--adjaceny-matrix") + 1]
                haveFile = True
            except:
                print("Command line arguments incorrect. 2")

    if "-f" in argv:
        try:
            inFile = argv[argv.index("-f") + 1]
            haveFile = True
            adjList = True
        except ValueError:
            print("Command line arguments incorrect. 3")

    if "-x" in argv or "--export" in argv:
        EXPORT = True
        try:
            inFile = argv[argv.index("-x") + 1]
            readInAdjFile(inFile)
            exportGraph()
            sys.exit(0)
        except ValueError:
            try:
                inFile = argv[argv.index("--export") + 1]
                readInAdjFile(inFile)
                exportGraph()
                sys.exit(0)
            except ValueError:
                print("Command line arguments incorrect. 3")

    if "--zdg" in argv:
        #run zdg generator
        n = argv[argv.index("--zdg") + 1]
        zeroDivisor(n)

    if "--random" in argv:
        #run random graph generator
        randroidGraph()

    if "-v" in argv or "--version" in argv:
        print("Graphworks 0.3.1")
        sys.exit(0)

    if "--gui" in argv:
        try:
            gui = True
            print("Start GUI")
            print("Nothing much yet. :)")
        except ValueError:
            print("Command line arguments incorrect. 4")

    if(adjList and haveFile):
        BUFFER.append("Reading in file...")
        readInAdjFile(inFile)
        BUFFER.append("Done.")
    elif(not adjList and haveFile):
        BUFFER.append("Reading in file...")
        readInMatrixFile(inFile)
        BUFFER.append("Done.")
    else:
        #if GUI was selected, try to run the GUI.
        if gui:
            # TODO
            print("GUI!")
        else:
            commandLine()

    #if all else fails, run the command line version.
    commandLine()


def readInAdjFile(inputFile):
    """Reads input file, sends to proper place. """

    global CURRENT
    inFile = open(inputFile, "r")
    d = {}
    for line in inFile:
        if line[0] == "#":
            continue

        if line.find("Name:") != -1:
            name = line[5:]
            CURRENT.setName(name)
            continue

        #Need to add re to take into account for ""*
        if line == "\n":
            continue
        if line.find("+DIRECTED") != -1:
            CURRENT.directed = True
            continue
        if line.find("+WEIGHTED") != -1:
            print("Weighted graphs can only be enterd with a matrix file.")
            sys.exit(1)

        key = line[0]
        data = line[4:].split()
        d[key] = data
    inFile.close()
    CURRENT.makeGraphList(d)
    if not EXPORT:
        init()


def readInMatrixFile(inputFile):
    inFile = open(inputFile, "r")
    row = []
    name = ""

    for line in inFile:
        if line[0] == "#":
            continue

        if line.find("Name:") != -1:
            name = line[5:]
            CURRENT.setName(name)
            continue

        #Need to add re to take int to account for ""*
        if line == "\n":
            continue

        if line.find("+DIRECTED") != -1:
            CURRENT.directed = True
            continue

        if line.find("+WEIGHTED") != -1:
            CURRENT.weighted = True
            continue

        row.append(line.split())

    matrix = numpy.array(row)
    CURRENT.makeGraphMatrix(matrix)
    inFile.close()
    init()

#6/6/06
#This needs fixing, for one, this currently just produces directed graphs. `


def randroidGraph():
    """Creates a random graph. """
    global CURRENT
    global DEBUG
    global BUFFER

    n = randrange(0, 20, 1)
    rMatrix = numpy.random.random((n, n))

    #Making sure the main diagonal has no ones in it.
    for x in range(n):
        if rMatrix[x, x] == 1:
            rMatrix[x, x] = 0

    CURRENT.makeGraphMatrix(rMatrix)
    init()
    CURRENT.name = "Random Graph"


def completeGraph():
    """Generates a complete graph of order n. """
    if POSIX:
        os.system("clear")
    else:
        os.system("cls")

    header()
    print()
    n = eval(input("How many nodes? "))
    completeGraph = (numpy.ones([n, n]) - numpy.identity(n))
    CURRENT.makeGraphMatrix(completeGraph)
    init()
    CURRENT.name = "K_" + str(n)


def newGraph():
    """Creates a blank new graph. """
    global CURRENT
    push()

    if POSIX:
        os.system("clear")
    else:
        os.system("cls")

    name = input("Name: ")
    GRAPHLST.append(CURRENT)
    CURRENT = Graph(name)


def init():
    """Performs several initial caculations with new graph."""
    global FUNCTHAND
    global CURRENT

    FUNCTHAND.graph = CURRENT
    FUNCTHAND.sparse()
    if FUNCTHAND.cycle():
        BUFFER.append("Has cycle(s)")
    else:
        BUFFER.append("Has no cycles.")

    #currently finds the number of paths between first key and last key.
    #BUFFER.append(FUNCTHAND.find_all_paths(CURRENT.adj.keys()[0],CURRENT.adj.keys()[-1],[]))


def stub():
    """This is just a stub function to provide some interface testing. """
    BUFFER.append("Not Implemented.")


def exit():
    """Called when exiting Graphworks. """
    sys.exit(0)


def trimBuffer():
    """Removes items from the message screen.  """
    if len(BUFFER) > 10:
        del BUFFER[1:2]


def exportGraph():
    """This function exports the current graph to the Graphviz standard layout.  """
    global CURRENT
    exportHandler = export.ExportHandler(CURRENT)
    exportHandler.makeGraphviz()
    file = exportHandler.getFileName()

    if not EXPORT:
        BUFFER.append("Export Done.")
        BUFFER.append("Graph deposited in " + file)


def saveGraph():
    """Saves the CURRENT graph into a *.gwk file. """

    exportHandler = export.ExportHandler(CURRENT)
    exportHandler.saveGraph()
    BUFFER.append(CURRENT.name.strip() + " saved.")


def printHelp():
    tmp = """
    (command) Name:  				Description.
    (1) New Graph:   				Create a new graph.
    (2) Functions:   				A list of various graph algorithms.
    (3) Utilities:   				Various utilities for working with Grapfwerk files.
    (4) Exit:        				Exit Graphworks.
    (clear) Clear:   				Clears message screen and possible your mind.
    (push) Push:     				Push current graph onto graph stack.
    (pop) Pop:       				Pop the graph off the top of the stack.
    (save) Save:	  				Saves current graph to a file of the same name.
    (export) Export: 				Exports Graph to Graphviz format for easy printing. Very low tariff.
    (new random) Random Graph:                      Create a random directed graph.
    (comp) Complement:			Generates the complement of the current graph.
    """
    BUFFER.append(tmp)


def clear():
    del BUFFER[1:]


def push():
    """Pushes the current graph onto the internal stack. """

    global CURRENT
    GRAPHLST.append(CURRENT)
    BUFFER.append(CURRENT.name.strip() + " pushed on stack.")
    CURRENT = Graph("Default")


def pop():
    """Pops the current graph from the internal stack. """

    global CURRENT
    CURRENT = GRAPHLST.pop()


def functionMenu():
    """Function handler menu. """

    global FUNCTHAND
    #Function Handler menu.
    while True:
        if POSIX:
            os.system("clear")
        else:
            os.system("cls")

        header()
        print("""
        Functions:
        1. Dominating Set
        2. All Paths
        3. Connected
        """)
        answer = input("Awaiting Your Command: ")

        try:
            {'1': FUNCTHAND.dom,
             '2': stub,
             '3': FUNCTHAND.connected,
             'exit': commandLine}[answer.strip().lower()]()
        except KeyError:
            BUFFER.append("Incorrect option.")


def header():
    """ Prints std header for graphworks. """
    global BUFFER
    print(f"\n\n\t\tGraphworks\t{graphworks.__version__}\n\n")
    print("\tCurrent Graph:")
    print("\t\t %s" % CURRENT)
    print()
    for line in BUFFER:
        print("\t%s" % line)


def renameGraph():
    """Renames the current graph. """
    newName = input("New name: ")
    CURRENT.name = newName.strip()

# TODO
# 1. Work on the numbering/naming scheme for the vertices.
# 2. Make sure the proper conditions are met through rigorous tests.


def cProduct():
    """
    Creates the cross product of two graphs.
    The two graphs being the CURRENT graph and the top graph on the stack.
    """
    global CURRENT
    if not GRAPHLST:
        BUFFER.append("Nothing on the stack.")
        return
    newList = {}

    list(CURRENT.adj.keys()).sort()
    list(GRAPHLST[0].adj.keys()).sort()

    # for the cartesian product to come out properly we have to
    # ensure the vertices don't have the same name.
    i = 1
    j = 0
    for key in list(CURRENT.adj.keys()):
        for k in list(GRAPHLST[0].adj.keys()):
            newList[(key + str(i), k + str(j))] = []
            j = j + 1
        i = i + 1
        j = 0

    n = []
    for key in list(newList.keys()):
        for k in list(newList.keys()):
            if key == k:
                continue
            if ((key[0] == k[0]) and (k[1].strip('0123456789') in GRAPHLST[0].adj[key[1].strip('0123456789')])) or ((key[1] == k[1]) and (k[0].strip('0123456789') in GRAPHLST[0].adj[key[0].strip('0123456789')])):
                n.append(str(k))
        newList[key] = deepcopy(n)
        n = []
    BUFFER.append(newList)

    tmpList = {}
    for key in list(newList.keys()):
        tmpList[str(key)] = newList[key]

    g = Graph(CURRENT.name + " X " + GRAPHLST[0].name)
    g.adj = tmpList
    #g.matrix = ???
    CURRENT = g


def complement():
    """Creates the complement graph of the current graph. """

    global CURRENT
    global BUFFER

    name = CURRENT.name
    size = CURRENT.matrix.shape[0]

    for x in range(size):
        for y in range(size):
            if CURRENT.matrix[x, y] == 1:
                CURRENT.matrix[x, y] = 0
            else:
                CURRENT.matrix[x, y] = 1

    newMatrix = CURRENT.matrix - numpy.identity(size)

    g = Graph("_" + name.strip() + "_")
    CURRENT = g
    CURRENT.makeGraphMatrix(newMatrix)
    init()


def zeroDivisor(n=None):
    """Creates a zero divisor graph for specified n. """

    global CURRENT

    if POSIX:
        os.system("clear")
    else:
        os.system("cls")

    header()

    print()
    if n is None:
        n = eval(input("Enter the modulus: "))

    alpha = "ABCDEFGIJKLMNOPQRSTUVWXYZ"
    numberLst = []
    zd = []
    # The final dictionary adjacency list for the zero divisor graph.
    zdgAdjList = {}
    # This describes how #'s are mapped to alpha characters in zero divisor graphs.
    zdgd = {}

    #excluding zero
    for i in range(1, n):
        numberLst.append(i)

    for i in numberLst:
        for j in numberLst:
            if (i * j) % n == 0:
                zd.extend([[i, j]])

    #removes double entries i.e. (10, 12) == (12, 10)
    for i in zd:
        x = i[1]
        y = i[0]
        a = [x, y]
        if a in zd:
            zd.remove(a)

    if zd == []:
        BUFFER.append("Z mod " + str(n) + " is an integral domain.")

    #This has to be here b/c Python doesn't destroy the above 'i'.
    i = 0
    for z in zd:
        if z[0] not in zdgd:
            zdgd[z[0]] = alpha[i]
            i = i + 1

        if z[1] not in zdgd:
            zdgd[z[1]] = alpha[i]
            i = i + 1

    for key in list(zdgd.keys()):
        tmp = []

        for k in zd:
            if k[0] == key:
                tmp.append(zdgd[k[1]])

            if k[1] == key:
                tmp.append(zdgd[k[0]])

        zdgAdjList[zdgd[key]] = deepcopy(tmp)

    CURRENT.name = "ZDG(" + str(n) + ")"
    CURRENT.makeGraphList(zdgAdjList)
    BUFFER.append("ZDG(" + str(n) + ") created.")


def commandLine():
    """The command line is the front line. """
    answer = ""
    #This is control loop of the program.
    while True:
        trimBuffer()
        if POSIX:
            os.system("clear")
        else:
            os.system("cls")
        header()
        print()
        print("\tCommands: ")
        print("\t\t1. New Graph ")
        print("\t\t2. Functions")
        print("\t\t3. Utilities")
        print("\t\t4. Exit\n ")

        answer = input("Awaiting Your Command: ")

        # Python flavored switch statement. May have to implement this statement
        # differently to allow for easier cli usage. i.e. so some functions can
        # have arguments passed to them.
        try:
            {'1': stub,
             '2': functionMenu,
             '3': stub,
             '4': exit,
             'clear': clear,
             'comp': complement,
             'cprod': cProduct,
             'exit': exit,
             'export': exportGraph,
             'export all': stub,
             'help': printHelp,
             'new': stub,
             'new random': randroidGraph,
             'push': push,
             'pop': pop,
             'rename': renameGraph,
             'new complete': completeGraph,
             'save': saveGraph,
             'utils': stub,
             'zdg': zeroDivisor
             }[answer.strip().lower()]()
        except KeyError:
            BUFFER.append("Incorrect option.")


if __name__ == "__main__":
    CURRENT = Graph("Default")
    GRAPHLST = []
    BUFFER = ["Messages:"]
    FUNCTHAND = FunctionHandler(BUFFER, CURRENT)
    DEBUG = False
    EXPORT = False
    if os.name == 'posix':
        POSIX = True
    else:
        POSIX = False

    main(sys.argv[1:])
