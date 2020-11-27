from typing import List

from .Vertex import VertexStatus, Vertex
from .Fire import Fire


class Graph:
    def __init__(self, compute_node):
        # mapping Vertex -> [Vertex]
        self.graph = {}
        self.fire = Fire(self)
        self.compute_node = compute_node
        self.burned_vertices = {}

    def init_fire(self):
        self.fire.start_burning()

    def stop_fire(self):
        self.fire.stop_burning()

    def get_vertex_status(self, vertex: Vertex):
        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                return vert.status
        return VertexStatus.DOESNT_EXIST

    def set_vertex_status(self, vertex: Vertex, status: VertexStatus):
        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                vert.status = status
                if status == VertexStatus.BURNED or status == VertexStatus.BURNING:
                    self.burned_vertices[vertex.vertex_id]

    def get_burned_vertices(self) -> list:
        return self.burned_vertices

    def get_neighbors(self, vertex: Vertex) -> [Vertex]:
        return self.graph[vertex]

    def add_vertex_and_neighbor(self, vertex_from: int, vertex_to: int):
        vertex = Vertex(vertex_from, 0)
        neighbor = Vertex(vertex_to, 0)
        if vertex in self.graph:
            self.graph[vertex].add(neighbor)
        else:
            self.graph[vertex] = [neighbor]

    def get_neighbors_to_burn(self, vertex: Vertex) -> List[Vertex]:
        all_neighbors = self.graph[vertex]
        neighbors_to_burn = list(filter(lambda vert: vert.status == VertexStatus.NOT_BURNED, all_neighbors))
        if len(neighbors_to_burn) == 0:
            return list()
        return neighbors_to_burn

    def spread_fire_to_other_nodes(self, burning_vertices: List[Vertex]) -> List[Vertex]:
        local_neighbors_to_burn = []
        for vertex in burning_vertices:
            # if the vertex is not in the graph, then it belongs to another partition
            # tell the compute node to handle the communication
            if self.compute_node.is_local(vertex.vertex_id):  # if vertex not in self.graph.keys()
                self.compute_node.send_burn_request(
                    vertex.vertex_id)  # can be optimised that smaller msgs can be combined
            else:
                local_neighbors_to_burn.add[vertex]
        return local_neighbors_to_burn

    def set_all_vertex_status(self, vertex_status: VertexStatus):
        for vertex in self.graph.keys():
            vertex.vertex_status = vertex_status

    def recreate_fire(self):
        self.stop_fire()
        self.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.init_fire()


class GraphInterpreter:
    """
    Responsible for interpreting graph data sets and returning an iterable.
    where every element is a string that looks like "vertex_id vertex_id",
    where an edge exists between the two vertex id's.
    """
    def __init__(self):
        pass

    def data_only(file) -> str:
        for line in file:
            if not line.startswith("#"):
                yield line

    def read_graph_file(self, file):
        data_only(file)
