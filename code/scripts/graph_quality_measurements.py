# run with python 2.7

import networkx as nx
import random
import argparse
import sys

calls = 0

def load_graph(vertex_file, edge_file):
    G = nx.Graph()
    with open(vertex_file, "r+") as vertexes:
        for v in vertexes.readlines():
            G.add_node(int(v))
    with open(edge_file, "w+") as edges:
        for e in edges.readlines():
            e.split()
            v1 = e[0]
            v2 = e[1]
            G.add_edge(v1, v2)
    return G
    # random graph for testing
    # return nx.erdos_renyi_graph(100, 0.2)

# G_original = load_graph("original.v", "original.e")
# G_new = load_graph("new.v", "new.e")


# test if graph is biconnected
# returns bool
def is_biconnected(G):
    return nx.is_biconnected(G)

# test the diameter of the two graphs
# returns int
def get_diameter(G):
    try:
        diameter = nx.diameter(G)
    except nx.networkx.exception.NetworkXError as e:
        diamter = str(e)
    return diamter


# test node_connectivity
# returns int or maybe float?
def get_node_connectivity(G):
    return nx.node_connectivity(G)

# test clustering coefficient
def get_average_clustering_coefficient(G):
    return nx.average_clustering(G)

# test the vertex cover of both graphs
# for scaled graphs, makes sense if the set is of scale as well.
def get_min_edge_cover(G):
    try:
        min_edge_cover = nx.min_edge_cover(G)
    except nx.networkx.exception.NetworkXException as e:
        # could be a number of reasons
        min_edge_cover = str(e)
    return min_edge_cover


# test the average_neighbor_degree of each node
# returns a float? int?
def get_average_vertex_degree(G):
    total = 0
    for node in G:
        total += len(G[node])
    total /= len(G)
    return total

# check if the graph is planar (for upscaling)
def is_planar(G):
    return nx.check_planarity(G)[0]

def average_array_len_in_dict(key, g_dict):
    total = 0
    target_dict = g_dict[key]
    for new_key in target_dict.keys():
        total += len(target_dict[new_key])
    return total/len(list(target_dict.keys()))


def get_average_shortest_path(G):
    # returns shortest paths from src to dst for all src and dst nodes
    G_avg_shortest_paths = nx.shortest_path(G)
    total_avg_shortest_path = sum(map(lambda x: average_array_len_in_dict(x, G_avg_shortest_paths), G_avg_shortest_paths)) / len(list(G_avg_shortest_paths.keys()))
    return total_avg_shortest_path



def get_qualities(G):
    biconnected = is_biconnected(G)
    diameter = get_diameter(G)
    node_connectivity = get_node_connectivity(G)
    average_clustering_coefficient = get_average_clustering_coefficient(G)
    min_edge_cover = get_min_edge_cover(G)
    average_vertex_degree = get_average_vertex_degree(G)
    planar = is_planar(G)
    average_shortest_path = get_average_shortest_path(G)
    qualities = []
    qualities.append("biconnected".ljust(35) + str(biconnected))
    qualities.append("diameter".ljust(35) + str(diameter))
    qualities.append("node_connectivity".ljust(35) + str(node_connectivity))
    qualities.append("average_clustering_coefficient".ljust(35) + str(average_clustering_coefficient))
    qualities.append("min_edge_cover".ljust(35) + str(min_edge_cover))
    qualities.append("average_vertex_degree".ljust(35) + str(average_vertex_degree))
    qualities.append("planar".ljust(35) + str(planar))
    qualities.append("average_shortest_path".ljust(35) + str(average_shortest_path))
    return qualities


def write_qualities(qualities, file_name):
    f = open(file_name, "w+")
    for q in qualities:
        f.write(q + "\n")
    f.close()
    return

def create_filename_for_output(v_file):
    last_slash = v_file.rfind("/")
    dot_index = v_file.rfind(".")
    if last_slash >= 0:
        file_name = v_file[last_slash+1:dot_index] + "_graph_qualities.txt"
    else:
        file_name = v_file[:dot_index] + "_graph_qualities.txt"
    return file_name



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    print("-----------unpacking-----------")
    print("...")
    parser.add_argument("path_to_vertex_file")
    parser.add_argument("path_to_edge_file")
    args = parser.parse_args()
    the_graph = load_graph(args.path_to_vertex_file, args.path_to_edge_file)
    print("-----------done---------------")
    print("----running measurements------")
    qualities = get_qualities(the_graph)
    print("-----------done---------------")
    output_file_name = create_filename_for_output(args.path_to_vertex_file)
    print("-----writing to file----------")
    write_qualities(qualities, output_file_name)
    print("------------done--------------")











