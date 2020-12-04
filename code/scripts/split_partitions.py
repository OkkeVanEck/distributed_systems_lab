"""
Discription: 
    Split edge files and partition files per node
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

import argparse
import os
import re
from contextlib import ExitStack

from .convert_graph_format import parse_nse

class Splitter:
    def __init__(self, graph_name):
        self.graph_name = graph_name

    def get_partition_files_path(self):
        for fname in os.listdir(f"data/{self.graph_name}/"):
            m = re.match(rf'{self.graph_name}\.graph\.([0-9]+)p', fname)
            if m:
                n_partitions = m.group(1)
                yield f"data/{self.graph_name}/{fname}", n_partitions

    def create_folders(self, n_partitions):
        os.mkdir(f"data/{self.graph_name}/{n_partitions}-partitions/")
        # for i in range(n_partitions):
        #     os.mkdir(f"data/{self.graph_name}/{n_partitions}-partitions/node{i + 1}")

    def parse_partition(self, fp):
        vert_node_dict = dict()
        for vid, nid in enumerate(fp): 
            vert_node_dict[vid] = nid
        return vert_node_dict

    def parse_partitions(self):
        for partition_file_path, n_partitions in self.get_partition_files_path(self.graph_name):
            self.create_folders(n_partitions)
            with open(partition_file_path, 'r') as fp:
                vert_node_dict = self.parse_partition(fp)
                yield vert_node_dict, n_partitions

    def parse_edges(self):
        edges_file_path = f"data/{self.graph_name}/{self.graph_name}.e"
        with open(edges_file_path, "r") as fp:
            for edge in fp:
                yield edge

    def split(self):
        for vert_node_dict, n_partitions in self.parse_partitions():
            with ExitStack() as stack:
                # prepare and open .e and .p files for write
                partition_files_path = f"data/{self.graph_name}/{n_partitions}-partitions"
                node_edges_fnames = [f"{partition_files_path}/node{i + 1}.e" for i in range(n_partitions)]
                node_partition_fnames = [f"{partition_files_path}/node{i + 1}.p" for i in range(n_partitions)]
                fnames = [x for xs in zip(node_edges_fnames, node_partition_fnames) for x in xs]
                files = [stack.enter_context(open(fname), 'r') for fname in fnames]
                # iterate over original .e file
                for vert_1, vert_2 in parse_nse(self.graph_name):
                    # add to both edge files
                    node_id_1 = vert_node_dict[vert_1]
                    node_edges_file = files[node_id_1 * 2]
                    node_edges_file.write(f"{vert_1} {vert_2}\n")

                    node_id_2 = vert_node_dict[vert_2]
                    node_edges_file = files[node_id_2 * 2]
                    node_edges_file.write(f"{vert_2} {vert_1}\n")

                    # add to partition files
                    # for node_id_1, if vert_2 is not on the node, then add to the partition file
                    if node_id_2 != node_id_1:
                        node_partition_file = files[node_id_1 * 2 + 1]
                        node_partition_file.write(f"{vert_2}\n")

                    # for node_id_2, if vert_1 is not on the node, then add to the partition file
                    if node_id_1 != node_id_2:
                        node_partition_file = files[node_id_2 * 2 + 1]
                        node_partition_file.write(f"{vert_1}\n")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_name")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    splitter = Splitter(args.graph_name)
    splitter.split()
