import numpy as np
import threading
import gzip
import time

from .Graph import Graph, GraphInterpreter
from .Vertex import Vertex
from .Enums import MPI_TAG, VertexStatus


from mpi4py import MPI
comm = MPI.COMM_WORLD

def log(message):
    if (True):
        print(message)


class ComputeNode:
    def __init__(self, rank):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)

        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat, args=())
        self.nodes_sent_in_heartbeat = {}

        self.kill_received = False

        self.hard_threshold = 10

    def is_local(self, vertex_id):
        """
        - for partitioning, return True if vertex_id
        - belongs to the compute node.
        """
        if (vertex_id % 5 + 1) == self.rank:
            return True
        return False
        # return self.get_vertex_rank(vertex_id) == self.rank

    def init_partition(self, file):
        file_uncrompressed = gzip.open(file, 'rt')
        assigned_vertices = 0
        for line in self.graph_reader.read_graph_file(file_uncrompressed):
            vertex, neighbor = map(int, line.split())
            if self.is_local(vertex):
                self.partitioned_graph.add_vertex_and_neighbor(vertex, neighbor)
                assigned_vertices += 1
        log("assigned_vertices = " + str(assigned_vertices))

    
    def manage_fires(self):
        # init_fire returns when stop_fire is called
        # stop fire is called in the listening thread when either
        #     1. A kill message is sent
        #       - when kill is sent, all vertex statuses are set to NOT_BURNED
        #.      - the graph stops the fire and set graph.burned_vertices to {}
        #.      - and self.kill_received is set to True
        #.    2. A reset meesage is sent.
        #       - same as above except self.kill_received remains false
        #.      - therefore, a new fire is started on the current thread
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
        print("end of computing on node: " + str(self.rank))
        print("burned vertexes on this partition are")
        for v in self.partitioned_graph.get_burned_vertices():
            print(v)

    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        data = np.array([vertex_id], dtype=np.int)
        # find dest machine based on the vertex rank
        # dest = self.get_vertex_rank(vertex_id)
        # comm.send(vertex_id, dest=dest, tag=11)

    def send_heartbeat(self):
        """
        - something like this.
        - make sure to wrap it in a function that executes code below
        - at a standard interval.
        """
        while not self.kill_received:
            burned_vertices = self.partitioned_graph.get_burned_vertices()
            heartbeat_nodes = []
            for vertex in burned_vertices:
                if vertex not in self.nodes_sent_in_heartbeat:
                    heartbeat_nodes.append(vertex)
                    self.nodes_sent_in_heartbeat[vertex] = True

            # data = np.array(heartbeat_nodes, dtype=np.int)
            # comm.Send(data, dest=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE)

            if len(self.nodes_sent_in_heartbeat.keys()) >= self.hard_threshold:
                log("killing compute node: " + str(self.rank))
                self.kill_received = True
                self.partitioned_graph.stop_fire()

            time.sleep(2)

    def listen(self):
        while not self.kill_received:
            self.listen_for_burn_requests()
            self.listen_to_head_node()
            time.sleep(2)

        # listen to a burn request from another node
    def listen_for_burn_requests(self):
        pass
        # if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE):
        #     data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE)
        #     v = Vertex(data, 0)
        #     # if the vertex is burned, ignore the message
        #     if self.partitioned_graph.get_vertex_status(v) == VertexStatus.NOT_BURNED:
        #         self.partitioned_graph.fire.add_burning_vertex(data)
    
    def listen_to_head_node(self):
        pass
        # if comm.Iprobe(source=0,tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE):
        #     data = comm.recv(source=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE)
        #     if data == "KILL":
        #         # join all threads. (listening threads at least)
        #         # put machine in a more idle state???
        #         self.kill_received = True
        #         self.partitioned_graph.stop_fire()
        #     if data == "RESET":
        #         self.partitioned_graph.stop_fire()
        #         self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
            


