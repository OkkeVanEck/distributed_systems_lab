import numpy as np
import threading
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
        self.nodes_sent_in_heartbeat = {}
        self.edges_sent_in_heartbeat = []

        self.kill_received = False
        self.reset_received = False
        self.num_fires = 0
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
            return False
        return True

    def init_partition(self, file):
        i = 0
        for vert_1, vert_2 in self.graph_reader.read_graph_file(file):
            if self.rank == 1 and i % 1000000 == 0:
                log("still initing partition on computer 1")
            self.partitioned_graph.add_vertex_and_neighbor(vert_1, vert_2)
            i += 1
        if self.rank == 1:
            log("machine 1 fone partitioning")

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
        if self.fires_wild:
            # log("in send burn request")
            dest = self.machine_with_vertex[vertex_id]
            # log("going to send a fire to " + str(dest) + ". data is " + str(vertex_id))
            comm.send(vertex_id, dest=dest, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value)

    def reset_fire(self):
        self.partitioned_graph.stop_fire()
        self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.edges_sent_in_heartbeat = []
        self.nodes_sent_in_heartbeat = {}
        comm.send(None, dest=0, tag=MPI_TAG.RESET_ACK.value)
        self.reset_received = False

    def send_heartbeat(self):
        while not self.kill_received:
            if self.reset_received:
                # manage reset in heartbeat thread so that we don't send an edge from fire 1
                # in the heartbeats from fire #2
                log("reset fire called")
                self.reset_fire()
            else:
                # log("top of send heartbeat")

                burned_vertices = self.partitioned_graph.get_burned_vertices()
                # log("burned vertices are " + str(burned_vertices))
                burned_edges = self.partitioned_graph.get_burned_edges()
                # log("burned edges are " + str(burned_edges))
                heartbeat_nodes = set()
                heartbeat_edges = set()

                # find new nodes to send in a heartbeat
                new_vertices = set()
                for v in burned_vertices:
                    if v not in self.nodes_sent_in_heartbeat:
                        new_vertices.add(v)
                # log("new vertices is " + str(new_vertices))
                heartbeat_nodes.update(new_vertices)
                # log("updated heartbeat_nodes")
                for node in new_vertices:
                    self.nodes_sent_in_heartbeat[node] = True
                # log("made it here 1")

                # heartbeat nodes are new nodes burned.
                # TODO https://github.com/OkkeVanEck/distributed_systems_lab/issues/16
                #   Find a way to empty the burned_edges after every heartbeat.
                #   Okke: Also maybe consider using sets for self.partitioned_graph.burned_vertices and burned_edges.
                # log("self.edges_sent_in_heartbeat = " + str(self.edges_sent_in_heartbeat))
                # log("burned_edges = " + str(burned_edges))
                # log("heartbeat_nodes = " + str(heartbeat_nodes))
                # log("prints done")
                for e in burned_edges:
                    if e[1] in heartbeat_nodes:
                        heartbeat_edges.add((e[0], e[1]))
                        self.edges_sent_in_heartbeat.append(e)
                # heartbeat_edges.update(set(e for e in burned_edges if e[1] in heartbeat_nodes))


                # log("sending heartbeat. sender is " + str(self.rank))
                # log("sent heartbeat. burned vertices are " + str(burned_vertices))
                # log("sent heartbeat. burned edges are " + str(burned_edges))
                data = list(heartbeat_edges)
                # log("made data 1. looks like, " + str(data))
                data = np.array(data, dtype=np.int)
                comm.send(data, dest=0, tag=MPI_TAG.HEARTBEAT.value)
                if len(data) > 0:
                    log("full send. " + str(data) + " from machine " + str(self.rank))

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
            log("receieved reset signal")
            data = comm.recv(source=0, tag=MPI_TAG.RESET_FROM_HEAD_TAG.value)
            self.reset_received = True
        if comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value):
            # receive the message
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.KILL_FROM_HEAD.value)
            log("received a burn request " + str(data))
            # join all threads. (listening threads at least)
            # put machine in a more idle state???
            self.kill_received = True
            self.partitioned_graph.stop_fire()
