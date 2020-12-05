from typing import List

from Enums import VertexStatus
from Vertex import Vertex
from Fire import Fire


class Graph:
    def __init__(self, compute_node):
        # mapping Vertex -> [Vertex]
        self.graph = {}
        self.fire = Fire(self)
        self.compute_node = compute_node
        # dict of vertex_id's
        self.burned_vertices = {}
        self.burned_edges = []

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
        # TODO: Issue/Enhancement https://github.com/OkkeVanEck/distributed_systems_lab/issues/13

        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                # log("set vertex burned. vertex_id = " + str(vertex.vertex_id) + " machine rank = " + str(self.compute_node.rank))
                vert.status = status
                if status == VertexStatus.BURNED or status == VertexStatus.BURNING:
                    self.burned_vertices[vertex.vertex_id] = True
                    return
        # possible setting a remote vertex status from the fire
        # if that's the case, add burned_vertex here so that the 
        # edge can be sent
        self.burned_vertices[vertex.vertex_id] = True


    def add_burned_edge(self, vertex_from: Vertex, vertex_to: Vertex):
        self.burned_edges.append([vertex_from.vertex_id, vertex_to.vertex_id])

    def get_burned_vertices(self):
        return self.burned_vertices

    def get_burned_edges(self):
        return self.burned_edges

    def get_neighbors(self, vertex: Vertex) -> [Vertex]:
        return self.graph[vertex]

    def add_vertex_and_neighbor(self, vertex_from: int, vertex_to: int):
        # TODO: Issue https://github.com/OkkeVanEck/distributed_systems_lab/issues/14
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
            return []
        neighbors_to_burn = list(filter(lambda vert: vert.status == VertexStatus.NOT_BURNED,
            all_neighbors))
        if len(neighbors_to_burn) == 0:
            return []
        return neighbors_to_burn

    def spread_fire_to_other_nodes(self, burning_vertices: List[Vertex]) -> List[Vertex]:
        local_neighbors_to_burn = []
        remote_neighbors_to_burn = []
        for vertex in burning_vertices:
            # if the vertex is not in the graph, then it belongs to another partition
            # tell the compute node to handle the communication
            # if vertex not in self.graph.keys()
            if not self.compute_node.is_local(vertex.vertex_id):  
                # can be optimised that smaller msgs can be combined
                self.compute_node.send_burn_request(vertex.vertex_id)
                remote_neighbors_to_burn.append(vertex)
            else:
                local_neighbors_to_burn.append(vertex)
        return local_neighbors_to_burn, remote_neighbors_to_burn

    def check_vertex_status(self):
        all_burned = True
        for vertex in self.graph.keys():
            for neighbor in self.graph[vertex]:
                if neighbor.status != VertexStatus.NOT_BURNED:
                    all_burned = False
            if vertex.status != VertexStatus.NOT_BURNED:
                all_burned = False
        return all_burned

    def set_all_vertex_status(self, vertex_status):
        self.burned_vertices = {}
        self.burned_edges = []
        for vertex in self.graph.keys():
            for neighbor in self.graph[vertex]:
                neighbor.status = vertex_status
            vertex.status = vertex_status

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
            if line[0] == "#":
                continue
            yield line

    def read_graph_file(self, file_uncompressed):
        return self.data_only(file_uncompressed)
