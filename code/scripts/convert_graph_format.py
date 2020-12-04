"""
Discription: 
    Dataset format converter from NSE graph format to Metis graph format.
    Ignore all weights on the graph.

Input format:
    NSE: <v_id> <v_id>
         vertex index can start from any non-negative integer, and each edge just appear once
         used by LDBC Graphalytics

Output format:
    Metis: <v_id> <v_id> ... <v_id>
         vertex index starts from 1, line i contains all neighbours of vertex i
         first line gives metadata info: <n_vertices> <n_edges>
         used by KaHIP, Metis...
"""

import argparse
from functools import singledispatch

@singledispatch
def get_value_from_line(pos, line):
    raise TypeError

@get_value_from_line.register(int)
def _(pos, line):
    return int(line.strip().split(" ")[pos])

@get_value_from_line.register(slice)
def _(pos, line):
    return [int(x) for x in line.strip().split(" ")[pos]]

class Metis:
    def __init__(self, graph_name, n_vertices, n_edges):
        self.graph_name = graph_name
        self.n_vertices = n_vertices
        self.n_edges = n_edges
        self.data = [[] for _ in range(n_vertices + 1)]
        self.data[0] = [n_vertices, n_edges]

    def put(self, vertex_1, vertex_2):
        # print(vertex_1, vertex_2)
        self.data[vertex_1].append(vertex_2)
        self.data[vertex_2].append(vertex_1)

    def save(self):
        with open(f"data/{self.graph_name}/{self.graph_name}.graph", "w") as f:
            for line in self.data:
                f.write(' '.join(map(str, line)) + '\n')

def parse_metadata(graph_name):
    properties_file_path = f"data/{graph_name}/{graph_name}.properties"
    with open(properties_file_path, 'r') as fp:
        for line in fp:
            if "meta.vertices" in line:
                n_vertices = get_value_from_line(-1, line)
            if "meta.edges" in line:
                n_edges = get_value_from_line(-1, line)

    vertex_file_path = f"data/{graph_name}/{graph_name}.v"
    with open(vertex_file_path, 'r') as fp:
        # nse starts from n, metis starts from 1, so offset is n - 1
        offset = int(fp.readline().strip()) - 1

    return n_vertices, n_edges, offset

def parse_nse(graph_name):
    file_path = f"data/{graph_name}/{graph_name}.e"
    with open(file_path, 'r') as fp:
        for line in fp:
            v_1, v_2 = get_value_from_line(slice(0, 2), line)
            yield v_1, v_2

def convert(args):
    n_vertices, n_edges, offset = parse_metadata(args.graph_name)
    metis = Metis(args.graph_name, n_vertices, n_edges)
    for v_1, v_2 in parse_nse(args.graph_name):
        metis.put(v_1 - offset, v_2 - offset)
    metis.save()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_name")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    convert(parse_args())
