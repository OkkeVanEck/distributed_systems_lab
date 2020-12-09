"""
This file computes properties of a graph that is provided through a vertex and
edge file.
"""

import networkx as nx
import argparse
import json
import os


def parse_args():
    """ Parse arguments for running graph analysis. """
    parser = argparse. \
        ArgumentParser(description="Process vertex and edge file and analyse "
                                   "resulting graph.")
    parser.add_argument("v_path", type=str, help="Path to the vertex file")
    parser.add_argument("e_path", type=str, help="Path to the edge file")
    return parser.parse_args()


def load_graph(vertex_file, edge_file):
    """ Parses vertex and edge files into a graph. """
    G = nx.Graph()

    # Parse vertices.
    with open(vertex_file, "r+") as vertexes:
        for v in vertexes.readlines():
            v = v.strip()
            if v.isdigit():
                G.add_node(int(v))
            else:
                raise Exception(f"Please pass a vertex file with only integer "
                                f"vertices.\n{v.strip()} is not a digit.")

    # Parse edges.
    with open(edge_file, "w+") as edges:
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
    properties["vertex_count"] = nx.number_of_vertices(G)
    properties["edge_count"] = nx.number_of_edges(G)
    properties["density"] = nx.density(G)
    properties["diameter"] = nx.diameter(G)
    properties["component_count"] = nx.number_connected_components(G)
    properties["planar"] = nx.check_planarity(G)[0]
    properties["node_connectivity"] = nx.node_connectivity(G)
    properties["avg_node_degree"] = comp_average_vertex_degree(G)
    properties["avg_clustering_coefficient"] = nx.average_clustering(G)
    properties["shortest_path"] = nx.shortest_path_length(G)
    properties["avg_shortest_path"] = nx.average_shortest_path_length(G)
    properties["min_edge_cover"] = nx.min_edge_cover(G)
    properties["min_node_cover"] = nx.min_node_cover(G)
    properties["influential_node_count"] = len(nx.voterank(G))

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
    print("Compute graph from given files..")
    G = load_graph(args.v_path, args.e_path)

    # Compute properties of graph and store in dictionary.
    print("Compute properties of graph..")
    properties = compute_properties(G)

    # Store properties in an properties file.
    print("Storing properties in file..")
    write_properties(properties, args.v_path)
