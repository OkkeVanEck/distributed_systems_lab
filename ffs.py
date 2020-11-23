__LOCAL__ = True


import argparse
import gzip
import random
from enum import Enum
from typing import List, Set, Tuple, Dict

import numpy as np

if not __LOCAL__:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

fwd_burning_prob: float = 0.2
file = "path/to/graph_file"


def get_vertex_rank(vertex_id: int) -> int:
    return vertex_id % (size - 1) + 1


class Vertex_Status(Enum):
    NOT_BURNED = 0
    # Neighbours of Burning vertices can be Burned, Not Burned, or Burning.
    BURNING = 1
    # All neighbors of the vertex are either Burning or are also Burned
    # nothing uses BURNED yet, could be nice to use as an optimization
    BURNED = 2
    DOESNT_EXIST = 3


class Vertex:

    def __init__(self, vertex_id: int, status: Vertex_Status):
        self.vertex_id = vertex_id
        self.status = status


class Fire:

    def __init__(self, graph):
        self.burning_vertices = []
        self.received_stop_signal = False
        self.graph = graph

    def start_burning():
        ignite_random_node()
        spread()

    def add_burning_vertex(self, vertex_id: int):
        vertex = Vertex(vertex_id, Vertex_Status.BURNING)
        # do we need to consider locks here?
        # the spread is on another thread
        self.burning_vertices.add(vertex)

    # execute math to determine what neighbors to burn
    def determine_burn_list(self, neighbors: list):
        # from paper quoted by Yancheng uses negative binomial function
        n_neighbors_to_burn = min(np.random.negative_binomial(1, 1 - fwd_burning_prob), len(neighbors))
        neighbors_to_burn = random.sample(neighbors, n_neighbors_to_burn) 
        return neighbors_to_burn

    def ignite_random_node(self):
        if len(self.burning_vertices) == 0:
            self.burning_vertices = random.sample(list(filter(lambda x: x.status == Vertex_Status.NOT_BURNED, self.graph.keys())), 1)

    def spread(self):
        # Every burn step adds new burning_vertices to the
        # burning vertices list. This will maintain burning order until there are no
        # more vertices to burn on the assigned partition.
        # 
        while(len(self.burning_vertices) > 0 and not self.received_stop_signal):
            vertex = self.burning_vertices[0]
            neighbors = self.graph.get_neighbors_to_burn(vertex.vertex_id)

            neighbors_to_burn = self.determine_burn_list(neighbors)
            self.graph.set_vertex_status(neighbors_to_burn, Vertex_Status.BURNING)
            self.graph.spread_fire_to_other_nodes(neighbors_to_burn)
            for new_burning_vertex in neighbors_to_burn:
                self.burned_vertices.add(new_burning_vertex)
            self.burned_vertices.pop(0)
        if not self.received_stop_signal:
            ignite_random_node()
            spread()

    def stop_burning(self):
        self.burning_vertices = []
        self.received_stop_signal = True
        

class Graph:
    
    def __init__(self, compute_node):
        # mapping Vertex -> [Vertex]
        self.graph = {}
        self.fire = Fire(self)
        self.compute_node = compute_node

    def init_fire(self):
        self.fire.start_burning()

    def stop_fire(self):
        self.fire.stop_burning()

    def get_vertex_status(self, vertex_id: int):
        for vertex in self.graph.keys():
            if vertex.vertex_id == vertex_id:
                return vertex.status
        return Vertex_Status.DOESNT_EXIST

    def get_burned_vertices(self) -> list:
        burned_vertices = []
        for vertex in self.graph.keys():
            if (vertex.status == Vertex_Status.BURNED or vertex.status == Vertex_Status.BURNING):
                burned_vertices.add(vertex)
        return burned_vertices

    def get_neighbors(self, vertex: Vertex) -> [Vertex]:
        return self.graph[vertex]

    def add_vertex_and_neighbor(self, vertex_from: int, vertex_to: int):
        vertex = Vertex(vertex_from, 0)
        neighbor = Vertex(vertex_to, 0)
        if vertex in self.graph:
            self.graph[vertex].add(neighbor)
        else:
            self.graph[vertex] = [neighbor]


    def get_neighbors_to_burn(self, vertex: Vertex) -> list:
        all_neighbors = self.graph[vertex]
        neighbors_to_burn = list(filter(lambda vert: vert.status == Vertex_Status.NOT_BURNED, all_neighbors))
        if len(neighbors_to_burn) == 0:
            return list()
        return neighbors_to_burn

    def spread_fire_to_other_nodes(self, burning_vertices):
        for vertex in burning_vertices:
            # if the vertex is not in the graph, then it belongs to another partition
            # tell the compute node to handle the communication
            if vertex not in self.graph:
                self.compute_node.send_burn_request(vertex.vertex_id)



def data_only(file) -> str:
    for line in file:
        if not line.startswith("#"):
            yield line

# responsible for interpreting graph data sets
# and returning an iterable where every element is a string that looks like
# "vertex_id vertex_id"
# where an edge exists between the two vertex id's
class Graph_Interpreter:

    def __init__(self):
        pass

    def read_graph_file(self, file):
        data_only(file)



class Compute_node:

    def __init__(self, rank):
        self.rank = rank
        self.graph_reader = Graph_Interpreter()
        self.partitioned_graph = Graph(self)

    # for partitioning, return True if vertex_id
    # belongs to the compute node.
    def is_local(self, vertex_id: int) -> int:
        return get_vertex_rank(vertex_id) == self.rank

    def init_partition(self, file):
        file_uncrompressed = gzip.open(file, 'rt')
        for line in self.graph_reader.read_graph_file(file_uncrompressed):
            vertex, neighbor = map(int, line.split())
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)

    def send_burn_request(self, vertex_id):
        # check partition map
        # send burn request to node with partition that has vertex_id
        # something like this
        if not __LOCAL__:
            comm.Send([np.array(neighbor, 1, dtype=np.int), 1, MPI.INT], dest=get_vertex_rank(neighbor), tag=11)

    def listen_for_burn_requests(self):
        if not __LOCAL__:
            while comm.Iprobe(source=MPI.ANY_SOURCE, tag=11):
                vertex = np.empty(1, dtype=np.int)
                comm.Recv(vertex, MPI.ANY_SOURCE, 11)
                partitioned_graph.fire.add_burning_vertex(vertex[0])


    def send_heartbeat(self):
        # something like this.
        # make sure to wrap it in a function that executes code below
        # at a standard interval.
        if not __LOCAL__:
            comm.Send([np.array(len(vertexes_to_burn), dtype=np.int), 1, MPI.INT], dest=0, tag=12)


    def return_burned_vertices(self):
        pass
            


if __name__ == "__main__":
    if __LOCAL__:
        rank = 1
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("data")
        parser.add_argument("n_nodes")
        args = parser.parse_args()
    if rank == 0:
        print("init head node")
        # initialize a head node/head node class
    else:
        compute_node = Compute_node(rank)
        compute_node.init_partition(file)
        # these might all need to be on separate threads
        # compute_node.partitioned_graph.init_fire()
        # compute_node.listen_for_burn_requests()
        # compute.send_heartbeat()



