"""
Discription: 
    Dataset format converter from LDBC graph format to Metis graph format.
    Ignore all weights on the graph.

LDBC graph format: <v_id> <v_id>
    vertex index is random non-negative integer, and each edge just appear once

Metis graph format: <v_id> <v_id> ... <v_id>
    vertex index starts from 1, line i contains all neighbours of vertex i
    first line gives metadata info: <n_vertices> <n_edges>
    used by KaHIP, Metis...
"""

from argparse import ArgumentParser
from graph_parser import GraphParser

METIS_N_LINES_OF_METADATA = 1

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    return args


def convert_ldbc_to_metis(graph_parser):
    # initialize metis graph data structure
    metis_data = [[] for i in range(graph_parser.n_vertices + METIS_N_LINES_OF_METADATA)]
    metis_data[0] = [graph_parser.n_vertices, graph_parser.n_edges]

    metis_by_ldbc = graph_parser.get_metis_by_ldbc()

    # put data into metis graph data structure
    for ldbc_vert_1, ldbc_vert_2 in graph_parser.lines_in_edge_file():
        metis_vert_1 = metis_by_ldbc(ldbc_vert_1) + METIS_N_LINES_OF_METADATA
        metis_vert_2 = metis_by_ldbc(ldbc_vert_2) + METIS_N_LINES_OF_METADATA
        
        metis_data[metis_vert_1].append(metis_vert_2)
        metis_data[metis_vert_2].append(metis_vert_1)

    # save data on disk
    with open(f"{graph_parser.path_to_graph}.m", "w") as f:
        for line in metis_data:
            f.write(' '.join(map(str, line)) + '\n')


if __name__ == '__main__':
    args = parse_args()
    graph_parser = GraphParser(args.name)
    convert_ldbc_to_metis(graph_parser)
