import numpy as np
import threading
import gzip
import time

from .Graph import Graph, GraphInterpreter
from .Vertex import Vertex
from .Enums import MPI_TAG, VertexStatus, SLEEP_TIMES

from mpi4py import MPI
comm = MPI.COMM_WORLD

DO_LOG=False


def log(message):
    if DO_LOG:
        print(message)


class ComputeNode:
    def __init__(self, rank, fires_wild, n_nodes):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.fires_wild = fires_wild
        self.num_compute_nodes = n_nodes - 1
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)

        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat,
                                                 args=())
        self.nodes_sent_in_heartbeat = {}
        self.edges_sent_in_heartbeat = []

        self.kill_received = False
        self.reset_received = False
        self.num_fires = 0
        self.allowed_fires = 1

        # for simulating without a HEAD NODE
        # self.hard_threshold = 10

    # TODO: https://github.com/OkkeVanEck/distributed_systems_lab/issues/15
    def machine_with_vertex(self, vertex_id):
        # add 1 because compute node rank starts at 1
        return (vertex_id % self.num_compute_nodes) + 1

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

        # TODO: Issue https://github.com/OkkeVanEck/distributed_systems_lab/issues/14
        for line in self.graph_reader.read_graph_file(file_uncompressed):
            vertex, neighbor = map(int, line.split())
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)
                assigned_vertices += 1

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
            # log("in manage fires")
            if self.num_fires < self.allowed_fires:
                self.partitioned_graph.init_fire()
                self.num_fires += 1
            else:
                time.sleep(SLEEP_TIMES.COMPUTE_NODE_MANAGE_FIRES.value)


    def do_tasks(self):
        self.listen_thread.start()
        self.heartbeat_thread.start()
        self.manage_fires()
        self.listen_thread.join()
        self.heartbeat_thread.join()
        # log("burned vertexes on this partition are")
        if DO_LOG:
            log("edges sent")
            for edge in self.edges_sent_in_heartbeat:
                log(edge)
            log("heartbeats nodes sent for machine " + str(self.rank) + " = " + str(len(self.nodes_sent_in_heartbeat)))


    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        # find dest machine based on the vertex rank
        if self.fires_wild:
            dest = self.machine_with_vertex(vertex_id)
            comm.send(vertex_id, dest=dest, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)

    def reset_fire(self):
        self.partitioned_graph.stop_fire()
        self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.num_fires = 0
        comm.send("", dest=0, tag=MPI_TAG.RESET_ACK.value)
        self.reset_received = False

    def send_heartbeat(self):
        while not self.kill_received:
            if self.reset_received:
                # manage reset in heartbeat thread so that we don't send an edge from fire 1
                # in the heartbeats from fire #2
                self.reset_fire()
            else:
                burned_vertices = self.partitioned_graph.get_burned_vertices()
                burned_edges = self.partitioned_graph.get_burned_edges()
                heartbeat_nodes = []
                heartbeat_edges = []

                # find new nodes to send in a heartbeat
                for vertex in burned_vertices:
                    if vertex not in self.nodes_sent_in_heartbeat:
                        heartbeat_nodes.append(vertex)
                        self.nodes_sent_in_heartbeat[vertex] = True

                # heartbeat nodes are new nodes burned.
                # TODO: https://github.com/OkkeVanEck/distributed_systems_lab/issues/16
                for vertex in heartbeat_nodes:
                    for edge in burned_edges:
                        if edge[1] == vertex and edge not in heartbeat_edges:
                            heartbeat_edges.append(edge)
                            self.edges_sent_in_heartbeat.append(edge)

                data = np.array(heartbeat_edges, dtype=np.int)
                comm.send(data, dest=0, tag=MPI_TAG.HEARTBEAT.value)

                # for simulations without head node object
                # if len(self.nodes_sent_in_heartbeat.keys()) >= self.hard_threshold:
                    # log("killing compute node: " + str(self.rank))
                    # self.kill_received = True
                    # self.partitioned_graph.stop_fire()

            time.sleep(SLEEP_TIMES.COMPUTE_NODE_SEND_HEARTBEAT.value)

    def listen(self):
        while not self.kill_received:
            # if fires aren't wild, no burn requests are sent.
            if self.fires_wild:
                self.listen_for_burn_requests()
            self.listen_to_head_node()
            time.sleep(SLEEP_TIMES.COMPUTE_NODE_LISTEN_SLEEP.value)

        # listen to a burn request from another node
    def listen_for_burn_requests(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)
            v = Vertex(data, 0)
            # if the vertex is burned, ignore the message
            if self.partitioned_graph.get_vertex_status(v) == VertexStatus.NOT_BURNED:
                self.partitioned_graph.fire.add_burning_vertex(data)


    def listen_to_head_node(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.RESET_FROM_HEAD_TAG.value):
            # receive the message so it doesn't idle out there
            data = comm.recv(source=0, tag=MPI_TAG.RESET_FROM_HEAD_TAG.value)
            self.reset_received = True
        if comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value):
            # receive the message
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value)
            # join all threads. (listening threads at least)
            # put machine in a more idle state???
            self.kill_received = True
            self.partitioned_graph.stop_fire()
