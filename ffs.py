import argparse
import gzip
import random
from typing import List, Set, Tuple, Dict

import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

neighbors: Dict[int, Set] = {}
statuses: Dict[int, int] = {}

parser = argparse.ArgumentParser()
parser.add_argument("data")
parser.add_argument("n_nodes")
args = parser.parse_args()

def is_local(vertex_id: int) -> int:
    return get_vertex_rank(vertex_id) == rank

def get_vertex_rank(vertex_id: int) -> int:
    return vertex_id % (size - 1) + 1

def data_only(file) -> str:
    for line in file:
        if not line.startswith("#"):
            yield line

def init():
    file = gzip.open(args.data, 'rt')
    for line in data_only(file):
        vertex, neighbor = map(int, line.split())
        if is_local(vertex):
            if vertex not in neighbors.keys():
                neighbors[vertex] = {neighbor}
            else:
                neighbors[vertex].add(neighbor)
            statuses[vertex], statuses[neighbor] = 0, 0
    file.close()

def get_neighbors_to_burn(vertex: int, fwd_burning_prob: float=0.2) -> set:
    neighbors_to_burn = list(filter(lambda x: statuses[x] == 0, neighbors[vertex]))
    if len(neighbors_to_burn) == 0:
        return set()
    n_neighbors_to_burn = min(np.random.negative_binomial(1, 1 - fwd_burning_prob), len(neighbors_to_burn))
    neighbors_to_burn = random.sample(neighbors_to_burn, n_neighbors_to_burn) 
    return set(neighbors_to_burn)

def ffs(scale_factor: float=0.5, fwd_burning_prob: float=0.2):
    if rank == 0:
        #TODO
    else:
        vertexes_to_burn = set(random.sample(list(filter(lambda x: statuses[x] == 0, neighbors.keys())), 1))
        neighbors_to_burn = set()
        while (True):
            for v in vertexes_to_burn:
                statuses[v] = 1
                neighbors_to_burn = neighbors_to_burn.union(get_neighbors_to_burn(v))
            neighbors_to_burn.clear()
            for neighbor in neighbors_to_burn:
                if is_local(neighbor):
                    vertexes_to_burn.add(neighbor)
                else:
                    comm.Send([np.array(neighbor, 1, dtype=np.int), 1, MPI.INT], dest=get_vertex_rank(neighbor), tag=11)
                    statuses[neighbor] = 1
            
            neighbors_to_burn.clear()

            while comm.Iprobe(source=MPI.ANY_SOURCE, tag=11):
                vertex = np.empty(1, dtype=np.int)
                comm.Recv(vertex, MPI.ANY_SOURCE, 11)
                vertexes_to_burn.add(vertex[0])
            
            while len(vertexes_to_burn) == 0:
                vertexes_to_burn = set(random.sample(list(filter(lambda x: statuses[x] == 0, neighbors.keys())), 1))


            comm.Send([np.array(len(vertexes_to_burn), dtype=np.int), 1, MPI.INT], dest=0, tag=12)

