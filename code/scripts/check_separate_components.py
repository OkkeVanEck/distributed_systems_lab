import networkx as nx
import sys
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("please add vertex and edge file")

vertexes = sys.argv[1]
print("vertex file = " + vertexes)
edges = sys.argv[2]
print("edge file = " + edges)


G = nx.Graph()
UG = G.to_undirected()
nodes_max = 2394385
nodes = set()
# print(nx.is_undirected(UG))
with open(vertexes, "r") as verts:
    for line in verts.readlines():
        nodes.add(int(line))
        if int(line) > nodes_max:
            continue
        else:
            UG.add_node(int(line))

node_id = 0
for node in sorted(list(nodes))[1:]:
    if node != node_id + 1:
        print("uh-oh dont have sequential nodes")
    node_id = node

print("nodes added = " + str(len(nodes)))

print("num lines is " + str(len(nodes)))
num_edges_added = 0
with open(edges, "r") as eds:
    for line in eds.readlines():
        line = line.split()
        fromm = int(line[0])
        to = int(line[1])
        if to < nodes_max and fromm < nodes_max:
            UG.add_edge(to, fromm)
            num_edges_added += 1

print("num_edges_added = " + str(num_edges_added))
edges_histogram = nx.degree_histogram(UG)
print("len of histogram is " + str(len(edges_histogram)))
plt.hist(edges_histogram, bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], range=(0, 16))
plt.show()
# print("num edges = " + str(nx.degree_histogram(UG)))
print(nx.is_directed(UG))
# make an undirected copy of the digraph
# UG = G.to_undirected()

# extract subgraphs
# sub_graphs = nx.connected_components(UG)
print(nx.is_connected(UG))
print(nx.number_connected_components(UG))
