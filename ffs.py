import argparse
import gzip
import random
from enum import Enum
from typing import List, Set, Tuple, Dict

import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


def get_vertex_rank(vertex_id: int) -> int:
    return vertex_id % (size - 1) + 1


class Vertex_Status(Enum):
    NOT_BURNED = 0
    # All neighbors of the vertex are either Burning or are also Burned
    BURNED = 1
    # Neighbours of Burning vertices can be Burned, Not Burned, or Burning.
    BURNING = 2
    DOESNT_EXIST = 3


class Vertex:
    vertex_id = 0
    status = 0


class Fire:
    burning_vertices = []
    received_stop_signal = False
    graph = Graph()

    def start_burning(graph: Graph):
        self.graph = Graph
        # TODO: pick a random vertex to start burning from
        # ranodom.seed(time)
        # random_vertex = random.random(len(self.graph.keys()))
        initial_vertex = self.graph.keys()[0]
        burning_vertices.add(vertex)
        spread()

    def add_burning_vertex(vertex_id):
        vertex = Vertex(vertex_id, Vertex_Status.BURNING)
        # do we need to consider locks here?
        # the spread is on another thread
        burning_vertices.add(vertex)

    def determine_burn_set(neighbors: Set):
        # from paper quoted by Yancheng uses negative binomial function
        n_neighbors_to_burn = min(np.random.negative_binomial(1, 1 - fwd_burning_prob), len(neighbors))
        neighbors_to_burn = random.sample(neighbors, n_neighbors_to_burn) 
        return set(neighbors_to_burn)

    def reignite():
        burning_vertices = set(random.sample(list(filter(lambda x: x.status == Vertex_Status.NOT_BURNED, graph.keys())), 1))

    def spread():
        # Every burn step adds new burning_vertices to the
        # burning vertices list. This will maintain burning order until there are no
        # more vertices to burn on the assigned partition.
        # 
        while(len(burning_vertices) > 0):
            vertex = burning_vertices[0]
            neighbors = graph.get_neighbors_to_burn(vertex.vertex_id)
            # from paper quoted by Yancheng uses negative binomial function
            neighbors_to_burn = determine_burn_set(neighbors)
            graph.set_vertex_status(neighbors_to_burn, Vertex_Status.BURNING)
            graph.spread_fire_to_other_nodes(neighbors_to_burn)
            for new_burning_vertex in neighbors_to_burn:
                burned_vertices.add(new_burning_vertex)
            burned_vertices.pop(0)
        if not received_stop_signal:
            reignite()
            spread()

    def stop_burning():
        burning_vertices = []
        received_stop_signal = True
        

class Graph:
    # mapping Vertex -> [Vertex]
    graph = {}
    fire = Fire()
    compute_node = Compute_node()

    def init_fire():
        fire.start_burning(self)

    def stop_fire():
        fire.stop_burning()

    def get_vertex_status(vertex_id: int):
        for vertex in graph.keys():
            if vertex.vertex_id == vertex_id:
                return vertex.status
        return Vertex_Status.DOESNT_EXIST

    def get_burned_vertices():
        burned_vertices = []
        for vertex in graph.keys():
            if (vertex.status == Vertex_Status.BURNED or vertex.status == Vertex_Status.BURNING):
                burned_vertices.add(vertex)
        return burned_vertices

    def get_neighbors(vertex: Vertex) -> [Vertex]:
        return graph[vertex]

    def add_vertex_and_neighbor(vertex_from: int, vertex_to: int):
        vertex = Vertex(vertex_from, 0)
        neighbor = Vertex(vertex_to, 0)
        if vertex in graph:
            graph[vertex].add(neighbor)
        else:
            graph[vertex] = [neighbor]


    def get_neighbors_to_burn(vertex: Vertex, fwd_burning_prob: float=0.2) -> set:
        all_neighbors = graph[vertex]
        neighbors_to_burn = list(filter(lambda vert: vert.status == Vertex_Status.NOT_BURNED, all_neighbors))
        if len(neighbors_to_burn) == 0:
            return set()
        return neighbors_to_burn
        
        n_neighbors_to_burn = min(np.random.negative_binomial(1, 1 - fwd_burning_prob), len(neighbors_to_burn))
        neighbors_to_burn = random.sample(neighbors_to_burn, n_neighbors_to_burn) 
        return set(neighbors_to_burn)

    def spread_fire_to_other_nodes(burning_vertices):
        for vertex in burning_vertices:
            if vertex not in graph:
                compute_node.send_burn_request(vertex.vertex_id)



def data_only(file) -> str:
    for line in file:
        if not line.startswith("#"):
            yield line

# responsible for interpreting graph data sets
# and returning an iterable where every element is a string that looks like
# "vertex_id vertex_id"
# where an edge exists between the two vertex id's
class graph_interpreter_manager:

    def read_graph_file(file):
        data_only(file)



class Compute_node:
    rank = 0
    graph_interpreter = graph_interpreter_manager()

    partitioned_graph = Graph()
    fires = []

    # for partitioning, return True if vertex_id
    # belongs to the compute node.
    def is_local(vertex_id: int) -> int:
        return get_vertex_rank(vertex_id) == rank

    def init_partition(file):
        # file = gzip.open(args.data, 'rt')
        for line in graph_interpreter.read_graph_file(file):
            vertex, neighbor = map(int, line.split())
            if is_local(vertex):
                partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)

    def send_burn_request(vertex_id):
        # check partition map
        # send burn request to node with partition that has vertex_id
        # something like this
        comm.Send([np.array(neighbor, 1, dtype=np.int), 1, MPI.INT], dest=get_vertex_rank(neighbor), tag=11)

    def listen_for_burn_requests():
        while comm.Iprobe(source=MPI.ANY_SOURCE, tag=11):
            vertex = np.empty(1, dtype=np.int)
            comm.Recv(vertex, MPI.ANY_SOURCE, 11)
            partitioned_graph.fire.add_burning_vertex(vertex[0])


    def send_heartbeat():
        # something like this.
        # make sure to wrap it in a function that executes code below
        # at a standard interval.
        comm.Send([np.array(len(vertexes_to_burn), dtype=np.int), 1, MPI.INT], dest=0, tag=12)


    def return_burned_vertices():

            


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("n_nodes")
    args = parser.parse_args()
    if rank == 0:
        # TODO
        # initialize a head node/head node class
    else:
        compute_node = Compute_node()
        compute_node.init_partition(file)
        # these might all need to be on separate threads
        compute_node.partitioned_graph.init_fire()
        compute_node.listen_for_burn_requests()
        compute.send_heartbeat()



