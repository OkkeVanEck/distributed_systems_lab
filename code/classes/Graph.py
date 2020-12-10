# import gzip

from typing import List

from Enums import VertexStatus
from Vertex import Vertex
from Fire import Fire


DO_LOG_GRAPH_CLASS=False


def log(message):
    if DO_LOG_GRAPH_CLASS:
        print(message)

class Graph:
    def __init__(self, compute_node):
        # mapping Vertex -> [Vertex]
        self.v_id_to_status = {}
        self.v_id_to_neighbors = {}
        self.compute_node = compute_node

    def set_vertex_status(self, vertex_id: int, status: VertexStatus):
        if vertex_id in self.v_id_to_status:
            self.v_id_to_status[vertex_id].status = status

    def get_vertex_status(self, vertex_id: int):
        return self.v_id_to_status[vertex_id].status

    def vert_exists_here(self, vertex_id):
        return vertex_id in self.v_id_to_status

    def get_neighbors(self, vertex_id: int) -> [int]:
        if vertex_id in self.v_id_to_neighbors:
            return self.v_id_to_neighbors[vertex_id]
        return []

    def get_neighbors_with_status(self, vertex_id: int, status: VertexStatus) -> [int]:
        neighbors = self.get_neighbors(vertex_id)
        ret = []
        for vert_id in neighbors:
            # if the neighbor vertex is local check the burn status
            if vert_id in self.v_id_to_status:
                if self.v_id_to_status[vert_id].status == status:
                    ret.append(vert_id)
            # if the neighbor is not local, add it to the burn
            # list anyway the fire will determine if it should
            # send a burn request
            else:
                ret.append(vert_id)
        return ret

    def add_vertex_and_neighbor(self, vertex_from: int, vertex_to: int):
        # first add vertex to status mapping
        vertex = Vertex(vertex_from, VertexStatus.NOT_BURNED)
        if vertex_from not in self.v_id_to_status:
            self.v_id_to_status[vertex_from] = vertex

        # then add vertex to adjacency list
        if vertex_from in self.v_id_to_neighbors:
            self.v_id_to_neighbors[vertex_from].add(vertex_to)
        else:
            self.v_id_to_neighbors[vertex_from] = set([vertex_to])

    def set_all_vertex_status(self, vertex_status):
        for v_id in self.v_id_to_status.keys():
            self.v_id_to_status[v_id].status = vertex_status

    def get_v_id_status_string(self):
        ret = ""
        for v_id in self.v_id_to_status:
            ret += str(v_id) + ": " + str(self.v_id_to_status[v_id].status) + "\n"
        return ret


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
