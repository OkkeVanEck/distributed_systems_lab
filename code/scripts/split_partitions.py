"""
Discription: 
    Split edge files and partition files per node

Details:
    For each edge, it should be in both edge files of the compute node of two vertices.
    In each line of the edge file of each node, the first vertex is guaranteed on the node, 
        the second vertex can be on the other node.
    In this way, each edge will appear twice but expressed in different vertex order.
    For partition file, it just contains the partition info of the vertices that 
        are not on the node but are neighbours of the vertices on this node.
    So for graph interpreter, it first reads the partition file, and then it reads the edge file. 
    When reading the edge file, it will:
        1. add the node rank as the partition info the vertex 1 (add to local vertices)
        2. add vertex 2 in the neighbour list of the vertex 1
        3. check if vertex 2 is in the partition file, if not add to local vertices
"""


import gzip
from argparse import ArgumentParser
from contextlib import ExitStack

from graph_parser import GraphParser

WORKER_NODES_RANK_OFFSET = 1

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("n_partition")
    args = parser.parse_args()
    return args

def split_partitions_and_edge_files(graph_parser, n_partition):
    path_to_partition_file = f"{graph_parser.path_to_graph}.m.{n_partition}p"
    with open(path_to_partition_file, 'r') as fp:
        vertice_ranks_mapping = graph_parser.get_vertice_ranks_mapping(fp)

    with ExitStack() as stack:
        paths_to_edge_files_on_nodes = \
            [f"{graph_parser.path_to_graph}-{n_partition}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.e.gz" \
                for i in range(n_partition)]
        paths_to_partition_files_on_nodes = \
            [f"{graph_parser.path_to_graph}-{n_partition}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.p.gz" \
                for i in range(n_partition)]
        
        edge_files_ptrs = [stack.enter_context(gzip.open(path_to_edge_file, 'wt')) \
                            for path_to_edge_file in paths_to_edge_files_on_nodes]
        partition_files_ptrs = [stack.enter_context(gzip.open(path_to_partition_file, 'wt')) \
                            for path_to_partition_file in paths_to_partition_files_on_nodes]

        # partition data will be duplicate, so write to a set instead of files directly
        partition_data = [set() for i in range(n_partition)]

        for vert_1, vert_2 in graph_parser.lines_in_edge_file():
            rank_for_vert_1 = vertice_ranks_mapping[vert_1]
            edge_files_ptrs[rank_for_vert_1].write(f"{vert_1} {vert_2}\n")

            rank_for_vert_2 = vertice_ranks_mapping[vert_2]
            edge_files_ptrs[rank_for_vert_2].write(f"{vert_2} {vert_1}\n")

            if rank_for_vert_1 != rank_for_vert_2:
                partition_data[rank_for_vert_1].add(f"{vert_2} {rank_for_vert_2 + WORKER_NODES_RANK_OFFSET}\n")
                partition_data[rank_for_vert_2].add(f"{vert_1} {rank_for_vert_1 + WORKER_NODES_RANK_OFFSET}\n")

        for data, fp in zip(partition_data, partition_files_ptrs):
            for line in data:
                fp.write(line)

if __name__ == "__main__":
    args = parse_args()
    graph_parser = GraphParser(args.name)
    split_partitions_and_edge_files(graph_parser, int(args.n_partition))
