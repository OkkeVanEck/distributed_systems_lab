"""
Discription: 
    Class for NSE graph data parser.  
"""


import os
import re
from argparse import ArgumentParser
from functools import singledispatch
from pathlib import Path


@singledispatch
def get_value_from_line(pos, line):
    raise TypeError

@get_value_from_line.register(int)
def _(pos, line):
    return int(line.strip().split(" ")[pos])

@get_value_from_line.register(slice)
def _(pos, line):
    return [int(x) for x in line.strip().split(" ")[pos]]

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    return args

class GraphParser:

    def __init__(self, name):
        self.name = name
        self.path_to_graph = f"data/{self.name}/{self.name}"

        # get #vertice and #edges
        with open(f"{self.path_to_graph}.properties", 'r') as fp:
            for line in fp:
                if "meta.vertices" in line:
                    self.n_vertices = get_value_from_line(-1, line)
                if "meta.edges" in line:
                    self.n_edges = get_value_from_line(-1, line)

        # get offset (nse starts from n; metis input file starts from 1, outputs file starts from 0)
        with open(f"{self.path_to_graph}.v", 'r') as fp:
            self.offset = get_value_from_line(0, fp.readline())

    def get_vertice_ranks_mapping(self, fp):
        vertice_ranks_mapping = dict()
        for vert_id, node_id in enumerate(fp): 
            vertice_ranks_mapping[vert_id + self.offset] = int(node_id)
        return vertice_ranks_mapping

    def lines_in_edge_file(self):
        with open(f"{self.path_to_graph}.e", 'r') as fp:
            for line in fp:
                vert_1, vert_2 = get_value_from_line(slice(0, 2), line)
                yield vert_1, vert_2

    def paths_to_partition_files(self):
        p = Path(".")
        for path_to_partition_file in p.glob(f"{self.path_to_graph}.m.*p"):
            path_to_partition_file = str(path_to_partition_file)
            m = re.match(rf'{self.path_to_graph}\.m\.([0-9]+)p', path_to_partition_file)
            n_partitions = int(m.group(1))
            yield path_to_partition_file, n_partitions

    def vertice_ranks_mappings(self):
        for path_to_partition_file, n_partitions in self.paths_to_partition_files():
            # os.mkdir(f"{self.path_to_graph}-{n_partitions}-partitions")
            with open(path_to_partition_file, 'r') as fp:
                vertice_ranks_mapping = self.get_vertice_ranks_mapping(fp)
                yield vertice_ranks_mapping, n_partitions


if __name__ == "__main__":
    pass