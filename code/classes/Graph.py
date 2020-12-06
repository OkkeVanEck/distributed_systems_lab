import gzip
from typing import List

from Enums import VertexStatus
from Vertex import Vertex
from Fire import Fire


DO_LOG_GRAPH_CLASS=True


def log(message):
    if DO_LOG_GRAPH_CLASS:
        print(message)

class Graph:
    def __init__(self, compute_node):
        # mapping Vertex -> [Vertex]
        self.graph = {}
        self.fire = Fire(self)
        self.compute_node = compute_node
        # dict of vertex_id's
        self.burned_vertices = set()
        self.burned_edges = set()

    def init_fire(self):
        self.fire.start_burning()

    def stop_fire(self):
        self.fire.stop_burning()

    def get_vert_list_with_burns_str(self, list):
        ret = ""
        for v in list:
            ret += str(v.vertex_id) + ":" + str(v.status.value) + " "
        return ret

    def print_with_burn(self):
        for v in self.graph.keys():
            print(str(v.vertex_id) + ":" + str(v.status.value) + " -> " + self.get_vert_list_with_burns_str(self.graph[v]))

    def get_vertex_status(self, vertex: Vertex):
        for vert in self.graph.keys():
            if vert.vertex_id == vertex.vertex_id:
                return vert.status
        return VertexStatus.DOESNT_EXIST

    def set_vertex_status(self, vertex_from: Vertex, vertex_to: Vertex, status: VertexStatus):
        # TODO: Issue/Enhancement https://github.com/OkkeVanEck/distributed_systems_lab/issues/13

        # burn into the direct neighor
        # i.e neighbor_list -> dict key
        vertex_from_neighbor_list = self.get_neighbors_list(vertex_from)
        for neighbor in vertex_from_neighbor_list:
            if neighbor.vertex_id == vertex_to.vertex_id:
                neighbor.status = status

        for vertex in self.graph.keys():
            if vertex.vertex_id == vertex_from.vertex_id:
                vertex.status = status
            if vertex.vertex_id == vertex_to.vertex_id:
                # log("set vertex burned. vertex_id = " + str(vertex.vertex_id) + " machine rank = " + str(self.compute_node.rank))
                vertex.status = status
                # brun the neighbors edge to the original vertex
                if status == VertexStatus.BURNED or status == VertexStatus.BURNING:
                    self.burned_vertices.add(vertex_to.vertex_id)

        vertex_to_neighbor_list = self.get_neighbors_list(vertex_to)
        for neighbor in vertex_to_neighbor_list:
            if neighbor.vertex_id == vertex_from.vertex_id:
                neighbor.status = status

        # possible setting a remote vertex status from the fire
        # if that's the case, add burned_vertex here so that the 
        # edge can be sent
        self.burned_vertices.add(neighbor.vertex_id)


    def add_burned_edge(self, vertex_from: Vertex, vertex_to: Vertex):
        self.burned_edges.update([(vertex_from.vertex_id, vertex_to.vertex_id)])

    def get_burned_vertices(self):
        return self.burned_vertices

    def get_burned_edges(self):
        return self.burned_edges

    def get_neighbors(self, vertex: Vertex) -> [Vertex]:
        return self.graph[vertex]

    def get_neighbors_list(self, vertex: Vertex) -> [Vertex]:
        for v in self.graph.keys():
            if v.vertex_id == vertex.vertex_id:
                return self.graph[v]
        return []

    def add_vertex_and_neighbor(self, vertex_from: int, vertex_to: int):
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
            # log("no neighbors to burn on machine " + str(self.compute_node.rank))
            return []
        neighbors_to_burn = list(filter(lambda vert: vert.status == VertexStatus.NOT_BURNED,
            all_neighbors))
        if len(neighbors_to_burn) == 0:
            # log("no neighbors to burn on machine " + str(self.compute_node.rank))
            return []
        return neighbors_to_burn

    def spread_fire_to_other_nodes(self, burning_vertices: List[Vertex]) -> List[Vertex]:
        local_neighbors_to_burn = []
        remote_neighbors_to_burn = []
        for vertex in burning_vertices:
            # if the vertex is not in the graph, then it belongs to another partition
            # tell the compute node to handle the communication
            # if vertex not in self.graph.keys()
            # log("going to compute is local")
            if not self.compute_node.is_local(vertex.vertex_id):
                # log("computed is not local")  
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
        self.burned_vertices = set()
        self.burned_edges = set()
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

    def read_graph_file(self, file):
        with open(file, "r") as fp:
            for line in fp:
                vert_1, vert_2 = list(map(int, line.strip().split(" ")))
                yield vert_1, vert_2
