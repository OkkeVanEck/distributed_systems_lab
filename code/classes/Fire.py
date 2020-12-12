from typing import List
import numpy as np
import random

from EdgeSet import EdgeSet
from Enums import VertexStatus
from Vertex import Vertex


DO_LOG_FIRE_CLASS=True


def log(message):
    if DO_LOG_FIRE_CLASS:
        print(message)


class Fire:
    def __init__(self, compute_node, graph, fwd_burning_prob=0.7):
        """
        fwd_burning_prob=0.7 is recommendation from leskovec06, so average burns
        2.33 neighbors
        """
        self.compute_node = compute_node
        self.burning_vertex_ids = []
        self.received_stop_signal = False
        self.graph = graph
        self.fwd_burning_prob = fwd_burning_prob
        self.remote_vertices_to_burn = []
        self.remote_vertices_burned = set()
        self.relight_counter = 0

        self.relight_exponent = 4
        self.relight_backoff = 2**(self.relight_exponent + 1)
        self.spreads_without_relight = 0

    # execute math to determine what neighbors to burn
    def determine_burn_list(self, neighbors: List[Vertex]) -> List[Vertex]:
        # interpretation from ahmed11, n_neighbors_to_burn is a geometric
        # distributed rv and the given expectation is enough to characterize it
        # so, fwd_burning_prob / (1 - fwd_burning_prob) = 1 / p
        n_neighbors_to_burn = int(np.ceil(self.fwd_burning_prob * len(neighbors)))
        neighbors_to_burn = random.sample(neighbors, n_neighbors_to_burn)
        return neighbors_to_burn

    def ignite_random_node(self):
        nb_filter = lambda x: self.graph.v_id_to_status[x].status == VertexStatus.NOT_BURNED
        not_burned_vertex_ids = filter(nb_filter, self.graph.v_id_to_status.keys())
        not_burned_vertex_ids_lst = list(not_burned_vertex_ids)
        if len(not_burned_vertex_ids_lst) > 0:
            random_vertex_id = np.random.choice(not_burned_vertex_ids_lst, size=1)[0]
            self.burning_vertex_ids.append(random_vertex_id)
            self.graph.set_vertex_status(random_vertex_id, VertexStatus.BURNED)

    def fire_help(self):
        if len(self.burning_vertex_ids) > 0:
            self.relight_backoff -= 1
            if self.relight_backoff <= 1 and self.relight_exponent > 4:
                self.relight_exponent = self.relight_exponent - 1
                self.relight_backoff = 2**(self.relight_exponent+4)
        else:
            num_relights = 2**self.relight_exponent
            for i in range(num_relights):
                self.ignite_random_node()
                # make sure to burn 16* how many nodes we lit before
                # lowering the relight exponent
            self.relight_backoff = 2**(self.relight_exponent+4)
            self.relight_exponent += 1

    def spread(self, new_edges: EdgeSet):
        # Every burn step adds new burning_vertex_ids to the
        # burning vertices list. This will maintain burning order until there
        # are no more vertices to burn on the assigned partition.
        self.fire_help()
        if len(self.burning_vertex_ids) > 0:
            vertex_id = self.burning_vertex_ids.pop(0)
            # log("burning vertex_id is " + str(vertex_id))

            neighbors = self.graph.get_neighbors_with_status(vertex_id, VertexStatus.NOT_BURNED)
            burned_neighbors = self.graph.get_neighbors_with_status(vertex_id, VertexStatus.BURNED)
            neighbors_to_burn = self.determine_burn_list(neighbors)
            # log("neighbors to burn are " + str(neighbors_to_burn))

            for new_burning_vertex in neighbors_to_burn:
                # set neighbor vertex status in graph
                self.graph.set_vertex_status(new_burning_vertex, VertexStatus.BURNING)
                # always add the edge to the fire, even if the new_burning vertex is on another
                # machine.
                new_edges.add_edge(vertex_id, new_burning_vertex)
                self.burning_vertex_ids.append(new_burning_vertex)
                if not self.graph.vert_exists_here(new_burning_vertex) and \
                                    new_burning_vertex not in self.remote_vertices_burned:
                    # log("adding to remote_vertices_to_burn. " + str(new_burning_vertex))
                    self.remote_vertices_to_burn.append(new_burning_vertex)

            # there are cases where one vertex burns into two vertexes that are also
            # connected by an edge. That edge should also be included in heartbeats
            for neighbor in burned_neighbors:
                new_edges.add_edge(vertex_id, neighbor)
           
    def reset_remote_vertices_to_burn(self):
        self.remote_vertices_burned.update(self.remote_vertices_to_burn)
        self.remote_vertices_to_burn = []

    def merge(self, new_burning_nodes):
        num_verts_added = 0
        # log(self.compute_node.get_machine_log() + ". new burning nodes = " + str(new_burning_nodes))
        for vert in new_burning_nodes:
            if self.graph.get_vertex_status(vert) == VertexStatus.NOT_BURNED:
                self.burning_vertex_ids.append(vert)
                self.remote_vertices_burned.add(vert)
                self.graph.set_vertex_status(vert, VertexStatus.BURNED)
                num_verts_added += 1
        # log(self.compute_node.get_machine_log() + ". num burning verts added = " + str(num_verts_added))
        # log(self.compute_node.get_machine_log() + ". len(burning verts) = " + str(len(self.burning_vertex_ids)))


    def get_burning_vertex_ids(self):
        return self.burning_vertex_ids

    def stop_burning(self):
        self.burning_vertex_ids = []


