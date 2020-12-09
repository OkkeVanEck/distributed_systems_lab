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
"""

# import gzip
from argparse import ArgumentParser
from contextlib import ExitStack

from graph_parser import GraphParser

WORKER_NODES_RANK_OFFSET = 1


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("n_part")
    args = parser.parse_args()
    return args


def split_partitions(graph_parser, n_part):
    rank_by_metis_vert = graph_parser.get_rank_by_metis_vert(n_part)
    metis_by_ldbc = graph_parser.get_metis_by_ldbc()

    with ExitStack() as stack:
        paths_to_edge_files_on_nodes = \
            [f"{graph_parser.path_to_graph}-{n_part}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.e"
                for i in range(n_part)]
        paths_to_partition_files_on_nodes = \
            [f"{graph_parser.path_to_graph}-{n_part}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.p"
                for i in range(n_part)]
        
        edge_files_ptrs = [stack.enter_context(open(path_to_edge_file, 'w')) \
                            for path_to_edge_file in paths_to_edge_files_on_nodes]
        part_files_ptrs = [stack.enter_context(open(path_to_partition_file, 'w')) \
                            for path_to_partition_file in paths_to_partition_files_on_nodes]

        # partition data will be duplicate, so write to a set instead of files directly
        part_data = [set() for i in range(n_part)]

        for ldbc_vert_1, ldbc_vert_2 in graph_parser.lines_in_edge_file():
            metis_vert_1, metis_vert_2 = metis_by_ldbc[ldbc_vert_1], metis_by_ldbc[ldbc_vert_2]

            rank_for_metis_vert_1 = rank_by_metis_vert[metis_vert_1]
            edge_files_ptrs[rank_for_metis_vert_1].write(f"{ldbc_vert_1} {ldbc_vert_2}\n")

            rank_for_metis_vert_2 = rank_by_metis_vert[metis_vert_2]
            edge_files_ptrs[rank_for_metis_vert_2].write(f"{ldbc_vert_2} {ldbc_vert_1}\n")

            if rank_for_metis_vert_1 != rank_for_metis_vert_2:
                part_data[rank_for_metis_vert_1].add(f"{ldbc_vert_2} {rank_for_metis_vert_2 + WORKER_NODES_RANK_OFFSET}\n")
                part_data[rank_for_metis_vert_2].add(f"{ldbc_vert_1} {rank_for_metis_vert_1 + WORKER_NODES_RANK_OFFSET}\n")

        for data, fp in zip(part_data, part_files_ptrs):
            for line in data:
                fp.write(line)


if __name__ == "__main__":
    args = parse_args()
    graph_parser = GraphParser(args.name)
    split_partitions(graph_parser, int(args.n_part))
