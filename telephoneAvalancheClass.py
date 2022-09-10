from utility import *
import networkx as nx
from random import random
from random import sample
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

class TelephoneAvalanche:
    def __init__(self, nodes, edgePerNode, maxIteration, nCallsPerRound = 5, startNode = [0]):
        """Init and run the "telephone/mail avalanche"

        Args:
            nodes (int): Number of nodes
            edgePerNode (int): Minimum numder of edges per node
            maxIteration (int): Maximum iteration / calling rounds within the telephone avalanche
            nCallsPerRound (int, optional): Number of calls, that are made by each caller per round. Defaults to 5.
            startNode (list, optional): Starting node(s). Defaults to [0].
        """
        if not isinstance(startNode, list):
            startNode = list(map(int, str(startNode)))
        self.startNode = startNode
        self.maxIteration = maxIteration
        self.nCallsPerRound = nCallsPerRound
        self.nodes = nodes
        self.nCalls = np.zeros(nodes)
        self.graphIsConnected = False
        while self.graphIsConnected == False:
            self.create_graph(nodes, edgePerNode)
            self.check_for_connection()
        self.calling(self.maxIteration)

    def create_graph(self, numberOfNodes, edgePerNode):
        """Creates a random graph with numberOfNodes nodes and edgePerNode edges per node

        Args:
            numberOfNodes (int): Number of nodes that are part of the graph G
            edgePerNode (int): Number of edges per node, which are randomly chosen. Total amount of edges per node might be larger than edgePerNode
        """
        V = list([v for v in range(numberOfNodes)])
        V = dict.fromkeys(V)
        for entry in V.keys():
            randomSample = rndm_excl_sample(entry, range(numberOfNodes), edgePerNode)
            V[entry] = randomSample
        G = nx.Graph(V)
        self.G = G

    def check_for_connection(self):
        """Sets self.graphIsConnected to true, if all components of Graph self.G are connected.
        """
        self.graphIsConnected = nx.is_connected(self.G)
        # if self.graphIsConnected == False:
        #     print("Graph is not connected.")
        # else:
        #     print("Graph is connected.")

    def init_first_call(self, startNode):
        self.nCalls = np.zeros(self.nodes)
        for nodes in startNode:
            self.nCalls[nodes] = 1

    def calling(self, iterations):
        nodesReached_ = 0
        self.callHistory = np.zeros((iterations,self.nCalls.size))
        # calledInPastDict stores by whom the called person has been called by
        calledInPastDict = {node: [] for node in range(self.nodes)}
        for i in range(iterations):
            # calledInPastDict = {node: [] for node in range(self.nodes)}
            if i == 0:
                # i == 0 is the initializing-step
                self.init_first_call(self.startNode)
            elif i == 1:
                allCallers = np.argwhere(self.nCalls == 1).squeeze().tolist()
                if not isinstance(allCallers, list):
                    allCallers = list(map(int, str(allCallers)))
                callersDict = dict.fromkeys(allCallers)
                for caller in callersDict.keys():
                    allNeighbors = get_node_neighbors(self.G, caller)
                    try:
                        calledNeighbors = sample(allNeighbors, self.nCallsPerRound)
                    except ValueError:
                        calledNeighbors = allNeighbors
                    self.nCalls[calledNeighbors] += 1
                    for neighbor in calledNeighbors:
                        calledInPastDict[neighbor].append(caller)
            else:
                # Only people, who have been called in the last round, call
                callMask = np.logical_and(self.callHistory[i-2,:] == 0, self.callHistory[i-1,:] > 0)

                allCallers = np.argwhere(callMask).squeeze().tolist()
                if not isinstance(allCallers, list):
                    allCallers = list(map(int, str(allCallers)))
                callersDict = dict.fromkeys(allCallers)

                for caller in callersDict.keys():
                    allNeighbors = get_node_neighbors(self.G, caller)
                    calledByInPast = calledInPastDict[caller]
                    possibleNeighbors = list(set(allNeighbors) - set(calledByInPast))
                    try:
                        calledNeighbors = sample(possibleNeighbors, self.nCallsPerRound)
                    except ValueError:
                        calledNeighbors = possibleNeighbors
                    self.nCalls[calledNeighbors] += 1
                    for neighbor in calledNeighbors:
                        calledInPastDict[neighbor].append(caller)
            nodesReached = np.count_nonzero(self.nCalls > 0)
            if nodesReached_ == nodesReached:
                self.callHistory[i,:] = self.nCalls
                self.callHistory = np.delete(self.callHistory, np.s_[i:], axis = 0)
                if nodesReached < self.nodes:
                    print(f"Not all nodes were reached within {self.maxIteration} iterations.")
                else:
                    print(f"All nodes were reached within {i-1} round(s) of calling.")
                return 
            nodesReached_ = nodesReached
            self.callHistory[i,:] = self.nCalls

    def plot_graph(self):
        pos = nx.spring_layout(self.G)
        nx.draw_networkx(self.G, pos)
        plt.show()

    def max_over_time(self):
        self.maxOverTime = np.max(self.callHistory,axis = 1)
    def mean_over_time(self):
        self.meanOverTime = np.mean(self.callHistory,axis = 1)
    def reached_over_time(self):
        self.reachedOverTime = np.count_nonzero(self.callHistory > 0, axis = 1)
