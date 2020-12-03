from typing import List

from .Vertex import Vertex


class HeadGraph:
    def __init__(self, total_vertices):
        self.base_id = 0
        self.total_vertices = total_vertices;
        self.vertices = set()
        self.edges = set()
        self.written_to_file = set()

    def get_number_vertices(self):
        return len(vertices)

    def add_edge(self, vertex_from: int, vertex_to: int, base_id=self.base_id):
        src = vertex_from + base_id
        dest = vertex_to + base_id
        self.vertices.add(src)
        self.vertices.add(dest)
        self.edges.add(f"{src} {dest}")
        self.edges.add(f"{dest} {src}")

    def next_sample(self):
        self.base_id += total_vertices

    def write_to_file(self):
        pass
