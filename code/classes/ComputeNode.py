import numpy as np
import threading
import gzip
import time

from Graph import Graph, GraphInterpreter
from Vertex import Vertex
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES

from mpi4py import MPI
comm = MPI.COMM_WORLD

DO_LOG=True


def log(message):
    if DO_LOG:
        print(message)


class ComputeNode:
    def __init__(self, rank, fires_wild, n_comp_nodes, machine_with_vertex):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.fires_wild = fires_wild
        self.num_compute_nodes = n_comp_nodes
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)

        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat,
                                                 args=())
        self.nodes_sent_in_heartbeat = set()
        self.edges_sent_in_heartbeat = set()

        self.kill_received = False
        self.reset_received = False
        self.num_fires = 0
        self.heartbeat_sends_data = 0
        self.allowed_fires = 1

        self.machine_with_vertex = machine_with_vertex

        # for simulating without a HEAD NODE
        # self.hard_threshold = 10


    def is_local(self, vertex_id):
        """
        - for partitioning, return True if vertex_id
        - belongs to the compute node.
        """
        # partition file only contains neighbours on on the remote nodes
        if vertex_id in self.machine_with_vertex.keys():
            # log("adding vertex to machine " + str(self.rank))
            return False
        return True

    def init_partition(self, file):
        # file_uncompressed = open(file, 'rt')
        assigned_vertices = 0

        # TODO: Issue https://github.com/OkkeVanEck/distributed_systems_lab/issues/14
        for line in self.graph_reader.read_graph_file(file):
            vertex, neighbor = line
            # vertex, neighbor = map(int, line.split()[:2])
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)
                assigned_vertices += 1

        log("machine " + str(self.rank) + " has " + str(assigned_vertices) + " nodes")

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

    def do_tasks(self):
        log("doing tasks")
        self.listen_thread.start()
        self.heartbeat_thread.start()
        self.manage_fires()
        self.listen_thread.join()
        self.heartbeat_thread.join()
        if DO_LOG:
            log("edges sent")
            for edge in self.edges_sent_in_heartbeat:
                log(edge)
            log(f"heartbeats nodes sent for machine {self.rank} = "
                f"{len(self.nodes_sent_in_heartbeat)}")

    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        # find dest machine based on the vertex rank
        log("going to send burn request")
        if self.fires_wild:
            log("here")
            dest = self.machine_with_vertex[vertex_id]
            log("sending burn request to machine " + str(dest) + " from machine " + str(self.rank) + ". data is " + str(vertex_id))
            comm.send(vertex_id, dest=dest, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)

    def reset_fire(self):
        self.partitioned_graph.stop_fire()
        self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.edges_sent_in_heartbeat = set()
        self.nodes_sent_in_heartbeat = set()
        comm.send("", dest=0, tag=MPI_TAG.RESET_ACK.value)
        self.reset_received = False

    def send_heartbeat(self):
        while not self.kill_received:
            # log("top of send heartbeaet")
            if self.reset_received:
                # manage reset in heartbeat thread so that we don't send an edge from fire 1
                # in the heartbeats from fire #2
                self.reset_fire()
            else:
                # burned vertices should be a set
                burned_vertices = self.partitioned_graph.get_burned_vertices()
                # log("burned_vertices are " + str(burned_vertices))
                # burned edges should be a set
                burned_edges = self.partitioned_graph.get_burned_edges()
                # log("burned edges are " + str(burned_edges))
                heartbeat_nodes = set()
                heartbeat_edges = set()

                # find new vertices to send in a heartbeat
                # log("self.nodes_sent_in_heartbeat is " + str(self.nodes_sent_in_heartbeat))
                # log("self.edges_sent_in_heartbeat is " + str(self.edges_sent_in_heartbeat))
                new_vertices = []
                for v in burned_vertices:
                    if v not in self.nodes_sent_in_heartbeat:
                        new_vertices.append(v)
                heartbeat_nodes.update(new_vertices)
                # log("heartbeat_nodes are " + str(heartbeat_nodes))

                self.nodes_sent_in_heartbeat.update(new_vertices)

                # heartbeat nodes are new nodes burned.
                # TODO https://github.com/OkkeVanEck/distributed_systems_lab/issues/16
                #   Find a way to empty the burned_edges after every heartbeat.
                #   Okke: Also maybe consider using sets for self.partitioned_graph.burned_vertices and burned_edges.
                new_edges = []
                for e in burned_edges:
                    if e not in self.edges_sent_in_heartbeat:
                        new_edges.append(e)
                heartbeat_edges.update(new_edges)
                # log("heartbeat_edges are " + str(heartbeat_edges))
                # heartbeat_edges.update(set(e for e in burned_edges if e[1] in heartbeat_nodes))
                self.edges_sent_in_heartbeat.update(new_edges)

                # log("sending heartbeat. sender is " + str(self.rank))
                # log("sent heartbeat. burned vertices are " + str(burned_vertices))
                # log("sent heartbeat. burned edges are " + str(burned_edges))
                data = np.array(list(heartbeat_edges), dtype=np.int)
                # log("made data: " + str(data) + ". len(data) is " + str(len(data)) + ". machine rank is " + str(self.rank))
                comm.send(data, dest=0, tag=MPI_TAG.HEARTBEAT.value)
                # if len(data) > 0: 
                #     log("have send valid data from machine " + str(self.rank))
                # self.heartbeat_sends_data += 1
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
            log("received burn requst data is " + str(data))
            v = Vertex(data, 0)
            log("made vertex")
            # if the vertex is burned, ignore the message
            if self.partitioned_graph.get_vertex_status(v) == VertexStatus.NOT_BURNED:
                log("adding received vertex to burning vertex list on machine " + str(self.rank))
                self.partitioned_graph.fire.add_burning_vertex(data)


    def listen_to_head_node(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.RESET_FROM_HEAD_TAG.value):
            # receive the message so it doesn't idle out there
            log("receieved reset signal")
            data = comm.recv(source=0, tag=MPI_TAG.RESET_FROM_HEAD_TAG.value)
            self.reset_received = True
        if comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value):
            # receive the message
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value)
            # join all threads. (listening threads at least)
            log("received kill")
            # put machine in a more idle state???
            self.kill_received = True
            self.partitioned_graph.stop_fire()
