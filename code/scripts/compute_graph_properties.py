"""
This file computes properties of a graph that is provided through a vertex and
edge file.
"""

import networkx as nx
import argparse
import json
import math
import os
from time import time


def valid_extension(path, extension):
    """ Checks whether a given path argument ends on the provided extension. """
    if not isinstance(path, str):
        raise argparse.ArgumentTypeError("Given file path is not a string")

    base, ext = os.path.splitext(path)
    if ext.lower() != extension:
        raise argparse.ArgumentTypeError(f"Extension of given file is not "
                                         f"{extension}")
    return path


def parse_args():
    """ Parse arguments for running graph analysis. """
    parser = argparse. \
        ArgumentParser(description="Process vertex and edge file and analyse "
                                   "resulting graph.")
    parser.add_argument("v_path", type=lambda a: valid_extension(a, ".v"),
                        help="Path to the vertex file")
    parser.add_argument("e_path", type=lambda a: valid_extension(a, ".e"),
                        help="Path to the edge file")
    return parser.parse_args()


def load_graph(vertex_file, edge_file):
    """ Parses vertex and edge files into a graph. """
    G = nx.Graph()

    # Parse edges.
    with open(edge_file, "r") as edges:
        for e in edges.readlines():
            v1, v2 = e.strip().split()
            G.add_edge(v1, v2)
    return G


def comp_average_vertex_degree(G):
    """ Compute average vertex degree of the vertices in the Graph G. """
    total = 0
    for node in G:
        total += len(G[node])
    total /= len(G)
    return total


def compute_properties(G):
    """ Compute properties of the given graph G. """
    properties = {}

    # First compute all functions that cannot give errors.
    start = time()
    print(f"Start: {start}")
    properties["vertex_count"] = nx.number_of_nodes(G)
    print(f"Vertex count: {time() - start}")
    properties["edge_count"] = nx.number_of_edges(G)
    print(f"Edge count: {time() - start}")
    properties["density"] = nx.density(G)
    print(f"Density: {time() - start}")
    properties["component_count"] = nx.number_connected_components(G)
    print(f"Component count: {time() - start}")
    # properties["planar"] = nx.check_planarity(G)[0]
    # print(f"Planarity: {time() - start}")
    properties["node_connectivity"] = nx.node_connectivity(G)
    print(f"Nodes connectivity: {time() - start}")
    properties["avg_node_degree"] = comp_average_vertex_degree(G)
    print(f"Avg node degree: {time() - start}")
    # properties["avg_clustering_coefficient"] = nx.average_clustering(G)
    # print(f"Avg clustering coefficient: {time() - start}")

    # Unconnected graph might give infinite path length exception.
    try:
        properties["diameter"] = nx.diameter(G)
    except nx.exception.NetworkXError:
        properties["diameter"] = math.inf
    print(f"Diameter: {time() - start}")

    # Unconnected graph has no average shortest path.
    try:
        properties["avg_shortest_path"] = nx.average_shortest_path_length(G)
    except nx.exception.NetworkXError:
        properties["avg_shortest_path"] = -math.inf
    print(f"Average shortest path: {time() - start}")

    # Graph has a node with no edge incident on it, so no edge cover exists.
    # try:
    #     properties["min_edge_cover"] = nx.min_edge_cover(G)
    # except nx.exception.NetworkXException:
    #     properties["min_edge_cover"] = -math.inf
    # print(f"Min edge cover: {time() - start}")

    return properties


def write_properties(properties, v_path):
    """ Write properties of graph to a properties file in JSON format. """
    filename = os.path.splitext(v_path)[0] + "_properties.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(properties, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Parse given arguments and error on failure.
    args = parse_args()

    # Load graph.
    print("\tLoad graph from given files..")
    start = time()
    G = load_graph(args.v_path, args.e_path)
    print(f"\nLoad graph total: {time() - start}")
    # Compute properties of graph and store in dictionary.
    print("\tCompute properties of graph..")
    properties = compute_properties(G)
    print(f"\nCompute properties total: {time() - start}")

    # Store properties in an properties file.
    print("\tStoring properties in file..")
    write_properties(properties, args.v_path)
