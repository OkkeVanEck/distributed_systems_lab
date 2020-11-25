import numpy as np
import gzip

from .Graph import Graph, GraphInterpreter


class ComputeNode:
    def __init__(self, rank, get_vertex_rank):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)
        self.get_vertex_rank = get_vertex_rank

    def is_local(self, vertex_id: int) -> int:
        """
        - for partitioning, return True if vertex_id
        - belongs to the compute node.
        """
        return self.get_vertex_rank(vertex_id) == self.rank

    def init_partition(self, file):
        file_uncrompressed = gzip.open(file, 'rt')
        for line in self.graph_reader.read_graph_file(file_uncrompressed):
            vertex, neighbor = map(int, line.split())
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)

    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        if not __LOCAL__:
            data = np.array([vertex_id], dtype=np.int)
            comm.Send([data, 1, MPI.INT], dest=self.get_vertex_rank(vertex_id), tag=11)

    def listen_for_burn_requests(self):
        if not __LOCAL__:
            while comm.Iprobe(source=MPI.ANY_SOURCE, tag=11):
                vertex = np.empty(1, dtype=np.int)
                comm.Recv(vertex, MPI.ANY_SOURCE, 11)
                partitioned_graph.fire.add_burning_vertex(vertex[0])

    def send_heartbeat(self):
        """
        - something like this.
        - make sure to wrap it in a function that executes code below
        - at a standard interval.
        """
        if not __LOCAL__:
            data = np.array(len(vertexes_to_burn), dtype=np.int)
            comm.Send([data, 1, MPI.INT], dest=0, tag=12)

    def return_burned_vertices(self):
        pass
