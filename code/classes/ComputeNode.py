import numpy as np
import threading
import gzip

from .Graph import Graph, GraphInterpreter
from .vertex import VertexStatus, Vertex
from .Enums import MPI_TAG


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

        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat, args())
        self.nodes_sent_in_heartbeat = {}

        self.receive_thread.start()
        self.kill_received = False

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

    
    def start_fire(self):
        self.listen_thread.start()
        self.heartbeat_thread.start()
        self.partitioned_graph.init_fire()
        self.listen_thread.join()
        self.heartbeat_thread.join()
        print("end of computing")

    def send_burn_request(self, vertex_id):
        """
        - check partition map
        - send burn request to node with partition that has vertex_id
        - something like this
        """
        data = np.array([vertex_id], dtype=np.int)
        # find dest machine based on the vertex rank
        dest = self.get_vertex_rank(vertex_id)
        comm.send(vertex_id, dest=dest, tag=11)

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
                    self.nodes_sent_in_heartbeat[vertex]

            data = np.array(heartbeat_nodes, dtype=numpy.int)
            comm.Send(data, dest=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE)
            time.sleep(2)

    def listen(self):
        while not self.kill_received:
            self.listen_for_burn_requests()
            self.listen_to_head_node()
            time.sleep(2)

        # listen to a burn request from another node
    def listen_for_burn_requests(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE)
            v = Vertex(data, 0)
            # if the vertex is burned, ignore the message
            if self.partitioned_graph.get_vertex_status(v) == VertexStatus.NOT_BURNED:
                self.partitioned_graph.fire.add_burning_vertex(data)
    
    def listen_to_head_node(self):
        if comm.Iprobe(source=0,tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE):
            data = comm.recv(source=0, tag=MPI_TAG.FROM_HEADNODE_TO_COMPUTE)
            if data == "KILL":
                # join all threads. (listening threads at least)
                # put machine in a more idle state???
                self.kill_received = True
                self.partitioned_graph.stop_fire()
            if data == "RESET":
                self.partitioned_graph.recreate_fire()
            


