#!/usr/bin/env python3
import functools
import itertools
from networkx import nx
from fractions import Fraction

def getpersonscontributedamount(whopaid, personId):
    return sum([v["amount"] for v in whopaid if v["personId"] == personId])

def solve_mincost_problem_for_expenses(job):
    nodes = [] # b cx cy
    for personId in job["people"]:
        nodes.append({"b": 0})
    
    G = nx.DiGraph()
    edges = [] # from to C L U
    for expense in job["expenses"]:
    
        whopaid = expense["whopaid"]
        whoshouldpay = expense["whoshouldpay"]
        total = functools.reduce(lambda accu, that: that["amount"] + accu, whopaid, 0)
    
        for v in range(len(nodes)):
            idealcontrib = Fraction(total , len(whoshouldpay)) if v in whoshouldpay else 0
            actualcontrib = getpersonscontributedamount(expense["whopaid"],v)
            diff = actualcontrib - idealcontrib
            #print(actualcontrib, idealcontrib, diff)
            nodes[v]["b"] += diff;

    for v, i in zip(nodes, itertools.count()):
        #print(job["people"][i], v["b"])
        G.add_node(job["people"][i], demand=v["b"])
    
    for i in range(len(job["people"])):
        for j in range(len(job["people"])):
            if (i != j):
                G.add_weighted_edges_from([(job["people"][i], job["people"][j], 1)])

    #print(G)
    flowCost, flowDict = nx.network_simplex(G)
    def conv_value_to_float(y):
        return (y[0], float(y[1]))
    flowDict = dict(map(lambda x: (x[0], dict(map(conv_value_to_float, x[1].items()))), flowDict.items())) # replace fractions with floats
    return flowDict

if __name__ == "__main__":
    people = ["janus", "tyk", "mads", "alex"]
    expenses = [{"whopaid": [{"personId": 0, "amount": 50},
        {"personId": 1, "amount": 30}
        ], "whoshouldpay": [0,1,2]}]
    job = {"expenses":expenses, "people": people}
    print(solve_mincost_problem_for_expenses(job))
