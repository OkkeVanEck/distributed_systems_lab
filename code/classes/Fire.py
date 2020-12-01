from typing import List
import numpy as np
import random

from .Enums import VertexStatus
from .Vertex import Vertex


class Fire:
    def __init__(self, graph, fwd_burning_prob=0.7):
        """
        fwd_burning_prob=0.7 is recommendation from leskovec06, so average burns
        2.33 neighbors
        """
        self.burning_vertices = []
        self.received_stop_signal = False
        self.graph = graph
        self.fwd_burning_prob = fwd_burning_prob

    def start_burning(self):
        self.ignite_random_node()
        self.spread()

    def add_burning_vertex(self, vertex_id: int):
        vertex = Vertex(vertex_id, VertexStatus.BURNING)
        # do we need to consider locks here?
        # the spread is on another thread
        self.burning_vertices.append(vertex)

    # execute math to determine what neighbors to burn
    def determine_burn_list(self, neighbors: List[Vertex]) -> List[Vertex]:
        # interpretation from ahmed11, n_neighbors_to_burn is a geometric
        # distributed rv and the given expectation is enough to characterize it
        # so, fwd_burning_prob / (1 - fwd_burning_prob) = 1 / p
        n_neighbors_to_burn = min(np.random.geometric(
            p=(1 - self.fwd_burning_prob) / self.fwd_burning_prob, size=1)[0],
                                  len(neighbors))
        neighbors_to_burn = random.sample(neighbors, n_neighbors_to_burn)
        return neighbors_to_burn

    def ignite_random_node(self):
        if len(self.burning_vertices) == 0:
            self.burning_vertices = random.sample(
                list(filter(lambda x: x.status == VertexStatus.NOT_BURNED,
                            self.graph.graph.keys())), 1)

    def spread(self):
        # Every burn step adds new burning_vertices to the
        # burning vertices list. This will maintain burning order until there
        # are no more vertices to burn on the assigned partition.
        while len(self.burning_vertices) > 0 and not self.received_stop_signal:
            vertex = self.burning_vertices[0]
            self.graph.set_vertex_status(vertex, VertexStatus.BURNED)
            neighbors = self.graph.get_neighbors_to_burn(vertex)
            neighbors_to_burn = self.determine_burn_list(neighbors)
            local_neighbors_to_burn = self.graph\
                .spread_fire_to_other_nodes(neighbors_to_burn)

            for new_burning_vertex in local_neighbors_to_burn:
                self.graph.set_vertex_status(new_burning_vertex,
                                             VertexStatus.BURNING)
                self.graph.add_burned_edge(vertex, new_burning_vertex)
                self.burning_vertices.append(new_burning_vertex)

            # if stop fire is called self.burning_vertices might have been set
            # to 0
            if len(self.burning_vertices) > 0:
                self.burning_vertices.pop(0)

        if not self.received_stop_signal:
            self.ignite_random_node()
            self.spread()

    def stop_burning(self):
        self.burning_vertices = []
        self.received_stop_signal = True
