from random import sample
import networkx as nx

def rndm_excl_sample(exclusiveValue, sampleRange, nSamples, maxIter = 100):
    # Initialize return sample
    i = 0
    returnSample = sample(sampleRange,nSamples)
    while exclusiveValue in returnSample and i < maxIter:
        returnSample = sample(sampleRange,nSamples)
        i += 1
    if i == maxIter:
        raise Warning("Sample could not be found. Function returns none.")
    else:
        # print(f"Sample found after {i} iterations.")
        return returnSample

def get_node_neighbors(graph,node):
    return list(nx.neighbors(graph,node))