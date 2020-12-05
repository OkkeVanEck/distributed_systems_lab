"""
Discription: 
    Dataset format converter from NSE graph format to Metis graph format.
    Ignore all weights on the graph.

NSE graph format: <v_id> <v_id>
    vertex index can start from any non-negative integer, and each edge just appear once
    used by LDBC Graphalytics

Metis graph format: <v_id> <v_id> ... <v_id>
    vertex index starts from 1, line i contains all neighbours of vertex i
    first line gives metadata info: <n_vertices> <n_edges>
    used by KaHIP, Metis...
"""


from .graph_parser import GraphParser, parse_args

METIS_VERTEX_ID_OFFSET = 1
METIS_N_LINES_OF_METADATA = 1

def convert_nse_to_metis(graph_parser):

    # initialize metis graph data structure
    metis_data = [[] for i in range(graph_parser.n_vertices + METIS_N_LINES_OF_METADATA)]
    metis_data[0] = [graph_parser.n_vertices, graph_parser.n_edges]

    # put data into metis graph data structure
    for vert_1, vert_2 in graph_parser.lines_in_edge_file():
        align_vert_1 = vert_1 - graph_parser.offset + METIS_VERTEX_ID_OFFSET
        align_vert_2 = vert_2 - graph_parser.offset + METIS_VERTEX_ID_OFFSET
        metis_data[align_vert_1].append(align_vert_2)
        metis_data[align_vert_2].append(align_vert_1)

    # save data on disk
    with open(f"{graph_parser.path_to_graph}.m", "w") as f:
        for line in metis_data:
            f.write(' '.join(map(str, line)) + '\n')


if __name__ == '__main__':
    args = parse_args()
    graph_parser = GraphParser(args.name)
    convert_nse_to_metis(graph_parser)
