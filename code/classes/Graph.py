from typing import List

from .Enums import VertexStatus
from .Vertex import Vertex
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
        self.burning_vertices = {}

    def get_vertex_status(self, vertex):
        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                return vert.status
        return VertexStatus.DOESNT_EXIST

    def set_vertex_status(self, vertex, status):
        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                vert.status = status
                if status == VertexStatus.BURNED or status == VertexStatus.BURNING:
                    self.burned_vertices[vertex.vertex_id] = True

    def get_burned_vertices(self):
        return self.burned_vertices

    def get_neighbors(self, vertex):
        return self.graph[vertex]

    def add_vertex_and_neighbor(self, vertex_from, vertex_to):
        vertex = Vertex(vertex_from, VertexStatus.NOT_BURNED)
        neighbor = Vertex(vertex_to, VertexStatus.NOT_BURNED)
        if vertex in self.graph:
            self.graph[vertex].append(neighbor)
        else:
            self.graph[vertex] = [neighbor]

    def get_neighbors_to_burn(self, vertex):
        # if a vertex isn't in the graph, it means it is on another partition
        # dont attempt to get its neighbors, just return an empty list
        if vertex in self.graph:
            all_neighbors = self.graph[vertex]
        else:
            return list()
        neighbors_to_burn = list(filter(lambda vert: vert.status == VertexStatus.NOT_BURNED, all_neighbors))
        if len(neighbors_to_burn) == 0:
            return list()
        return neighbors_to_burn

    def spread_fire_to_other_nodes(self, burning_vertices):
        local_neighbors_to_burn = []
        for vertex in burning_vertices:
            # if the vertex is not in the graph, then it belongs to another partition
            # tell the compute node to handle the communication
            # if vertex not in self.graph.keys()
            if self.compute_node.is_local(vertex.vertex_id):  
                # can be optimised that smaller msgs can be combined
                self.compute_node.send_burn_request(vertex.vertex_id)  
            else:
                local_neighbors_to_burn.append(vertex)
        return local_neighbors_to_burn

    def set_all_vertex_status(self, vertex_status):
        for vertex in self.graph.keys():
            vertex.vertex_status = vertex_status


class GraphInterpreter:
    """
    Responsible for interpreting graph data sets and returning an iterable.
    where every element is a string that looks like "vertex_id vertex_id",
    where an edge exists between the two vertex id's.
    """
    def __init__(self):
        pass

    def data_only(self, file):
        for line in file:
            check = line.decode('utf-8')
            if check[0] == "#":
                continue
            # print(check)
            yield check

    def read_graph_file(self, file_uncrompressed):
        # print("attempting to read")
        return self.data_only(file_uncrompressed)
