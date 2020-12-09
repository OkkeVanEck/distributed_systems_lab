"""
This file computes properties of a graph that is provided through a vertex and
edge file.
"""

import networkx as nx
import argparse
import json
import math
import os


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

    # Parse vertices.
    with open(vertex_file, "r") as vertices:
        for v in vertices.readlines():
            v = v.strip()
            if v.isdigit():
                G.add_node(int(v))
            else:
                raise Exception(f"Please pass a vertex file with only integer "
                                f"vertices.\n{v.strip()} is not a digit.")

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
    properties["vertex_count"] = nx.number_of_nodes(G)
    properties["edge_count"] = nx.number_of_edges(G)
    properties["density"] = nx.density(G)
    properties["component_count"] = nx.number_connected_components(G)
    properties["planar"] = nx.check_planarity(G)[0]
    properties["node_connectivity"] = nx.node_connectivity(G)
    properties["avg_node_degree"] = comp_average_vertex_degree(G)
    properties["avg_clustering_coefficient"] = nx.average_clustering(G)
    properties["influential_node_count"] = len(nx.voterank(G))

    # Unconnected graph might give infinite path length exception.
    try:
        properties["diameter"] = nx.diameter(G)
    except nx.exception.NetworkXError:
        properties["diameter"] = math.inf

    # Unconnected graph has no average shortest path.
    try:
        properties["avg_shortest_path"] = nx.average_shortest_path_length(G)
    except nx.exception.NetworkXError:
        properties["avg_shortest_path"] = -math.inf

    # Graph has a node with no edge incident on it, so no edge cover exists.
    try:
        properties["min_edge_cover"] = nx.min_edge_cover(G)
    except nx.exception.NetworkXException:
        properties["min_edge_cover"] = -math.inf

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
    print("Load graph from given files..")
    G = load_graph(args.v_path, args.e_path)

    # Compute properties of graph and store in dictionary.
    print("Compute properties of graph..")
    properties = compute_properties(G)

    # Store properties in an properties file.
    print("Storing properties in file..")
    write_properties(properties, args.v_path)
