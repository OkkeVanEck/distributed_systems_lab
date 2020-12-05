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


from contextlib import ExitStack

from .graph_parser import GraphParser, parse_args

WORKER_NODES_RANK_OFFSET = 1

def split_partitions_and_edge_files(graph_parser):

    for vertice_ranks_mapping, n_partitions in graph_parser.vertice_ranks_mappings():
        with ExitStack() as stack:
            # prepare and open .e and .p files for write
            paths_to_edge_files_on_nodes = \
                [f"{graph_parser.path_to_graph}-{n_partitions}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.e" \
                    for i in range(n_partitions)]
            paths_to_partition_files_on_nodes = \
                [f"{graph_parser.path_to_graph}-{n_partitions}-partitions/node{i + WORKER_NODES_RANK_OFFSET}.p" \
                    for i in range(n_partitions)]
            
            edge_files_ptrs = [stack.enter_context(open(path_to_edge_file), 'w') \
                                for path_to_edge_file in paths_to_edge_files_on_nodes]
            partition_files_ptrs = [stack.enter_context(open(path_to_partition_file), 'w') \
                                for path_to_partition_file in paths_to_partition_files_on_nodes]

            # iterate over original .e file
            for vert_1, vert_2 in graph_parser.lines_in_edge_file():
                # add to both edge files
                rank_for_vert_1 = vertice_ranks_mapping[vert_1]
                edge_files_ptrs[rank_for_vert_1].write(f"{vert_1} {vert_2}\n")

                rank_for_vert_2 = vertice_ranks_mapping[vert_2]
                edge_files_ptrs[rank_for_vert_2].write(f"{vert_2} {vert_1}\n")

                # add to partition files
                if rank_for_vert_1 != rank_for_vert_2:
                    partition_files_ptrs[rank_for_vert_1].write(f"{vert_2} {rank_for_vert_2 + WORKER_NODES_RANK_OFFSET}\n")
                    partition_files_ptrs[rank_for_vert_2].write(f"{vert_1} {rank_for_vert_1 + WORKER_NODES_RANK_OFFSET}\n")


if __name__ == "__main__":
    args = parse_args()
    graph_parser = GraphParser(args.name)
    split_partitions_and_edge_files(graph_parser)
    