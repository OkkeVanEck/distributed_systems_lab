import numpy as np
import threading
import gzip
import time

from .Graph import Graph, GraphInterpreter
from .Vertex import Vertex
from .Enums import MPI_TAG, VertexStatus

from mpi4py import MPI
comm = MPI.COMM_WORLD

DO_LOG=False


def log(message):
    if DO_LOG:
        print(message)


class ComputeNode:
    def __init__(self, rank, n_nodes):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)

        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat,
                                                 args=())
        self.nodes_sent_in_heartbeat = {}

        self.kill_received = False

        # for simulating without a HEAD NODE
        self.hard_threshold = 10

    def machine_with_vertex(self, vertex_id):
        return vertex_id % self.num_compute_nodes + 1

    def is_local(self, vertex_id):
        """
        - for partitioning, return True if vertex_id
        - belongs to the compute node.
        """
        if self.machine_with_vertex(vertex_id) == self.rank:
            return True
        return False

    def init_partition(self, file):
        file_uncompressed = gzip.open(file, 'rt')
        assigned_vertices = 0

        for line in self.graph_reader.read_graph_file(file_uncompressed):
            vertex, neighbor = map(int, line.split())
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)
                assigned_vertices += 1

        log("assigned_vertices = " + str(assigned_vertices))

    def manage_fires(self):
        # init_fire returns when stop_fire is called
        # stop fire is called in the listening thread when either
        #     1. A kill message is sent
        #       - when kill is sent, all vertex statuses are set to NOT_BURNED.
        #       - the graph stops the fire and set graph.burned_vertices to {}.
        #       - and self.kill_received is set to True.
        #     2. A reset message is sent.
        #       - same as above except self.kill_received remains false.
        #       - therefore, a new fire is started on the current thread.
        while not self.kill_received:
            self.partitioned_graph.init_fire()
        log("return from assigned_vertices")

    def do_tasks(self):
        log("do tasks for compute node; " + str(self.rank))
        self.listen_thread.start()
        self.heartbeat_thread.start()
        self.manage_fires()
        self.listen_thread.join()
        self.heartbeat_thread.join()
        log("end of computing on node: " + str(self.rank))
        log("burned vertexes on this partition are")
        for v in self.partitioned_graph.get_burned_vertices():
            log(v)

    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        # find dest machine based on the vertex rank
        dest = self.machine_with_vertex(vertex_id)
        log("sending burn request to machine " + str(dest) + ". data = " + str(vertex_id))
        comm.send(vertex_id, dest=dest, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)

    def send_heartbeat(self):
        while not self.kill_received:
            log("sending heartbeat")
            burned_vertices = self.partitioned_graph.get_burned_vertices()
            burned_edges = self.partitioned_graph.get_burned_edges()
            heartbeat_nodes = []
            heartbeat_edges = []

            # find new nodes to send in a heartbeat
            for vertex in burned_vertices:
                if vertex not in self.nodes_sent_in_heartbeat:
                    heartbeat_nodes.append(vertex)
                    self.nodes_sent_in_heartbeat[vertex] = True

            # find the edges
            for vertex in heartbeat_nodes:
                for edge in burned_edges:
                    if edge[1] == vertex:
                        heartbeat_edges.append(edge)

            data = np.array(heartbeat_edges, dtype=np.int)
            comm.send(data, dest=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE.value)

            # for simulations without head node object
            if len(self.nodes_sent_in_heartbeat.keys()) >= self.hard_threshold:
                log("killing compute node: " + str(self.rank))
                self.kill_received = True
                self.partitioned_graph.stop_fire()

            time.sleep(2)

    def listen(self):
        while not self.kill_received:
            log("checking if other messages arrived")
            self.listen_for_burn_requests()
            self.listen_to_head_node()
            time.sleep(0.05)

        # listen to a burn request from another node
    def listen_for_burn_requests(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)
            v = Vertex(data, 0)
            # if the vertex is burned, ignore the message
            if self.partitioned_graph.get_vertex_status(v) == VertexStatus.NOT_BURNED:
                log("received burn request on computer " + str(self.rank) + ". data = " + str(data))
                self.partitioned_graph.fire.add_burning_vertex(data)

    def listen_to_head_node(self):
        if comm.Iprobe(source=0,tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE.value):
            data = comm.recv(source=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE.value)
            if data == "KILL":
                # join all threads. (listening threads at least)
                # put machine in a more idle state???
                self.kill_received = True
                self.partitioned_graph.stop_fire()
            if data == "RESET":
                self.partitioned_graph.stop_fire()
                self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
