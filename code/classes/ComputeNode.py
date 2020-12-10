import numpy as np
import time

from Graph import Graph, GraphInterpreter
from Fire import Fire
from EdgeSet import EdgeSet
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
        self.killed = False
        self.fires_wild = fires_wild
        self.num_compute_nodes = n_comp_nodes
        self.graph_reader = GraphInterpreter()
        self.partitioned_graph = Graph(self)
        self.fire_step = 10
        self.fire = Fire(self, self.partitioned_graph)
        self.machine_with_vertex = machine_with_vertex

    def get_machine_log(self):
        return "On Machine " + str(self.rank) + "."


    def send_fire_to_remotes(self, machine_vertexes_to_receive):
        nodes_to_burn_locally = []
        # log(self.get_machine_log() + " sending data")

        for i in range(1, self.num_compute_nodes+1):
            if i != self.rank:
                # log(self.get_machine_log() + " machine_vertexes_to_receive[" + str(i) + "] = " + str(len(machine_vertexes_to_receive[i])))
                data = comm.sendrecv(machine_vertexes_to_receive[i],
                    dest=i ,
                    sendtag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value,
                    recvbuf=None,
                    source=i,
                    recvtag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value,
                    status=None)
                # log("On machine " + str(self.rank) + ". Sent data " + str(machine_vertexes_to_receive[i]))
                # log("On machine " + str(self.rank) + ". Received data " + str(list(data)))
                if len(data) > 0:
                    # log(self.get_machine_log() + " recieved data with length " + str(len(data)))
                    nodes_to_burn_locally.extend(data)

        # log("done sending/receiving on machine " + str(self.rank))
        self.fire.merge(nodes_to_burn_locally)


    def send_heartbeat(self, new_edges):
        # this send is non-blocking
        # log("sending heartbeat")
        if self.rank == 2 or self.rank == 3:
            if self.fire.relight_counter > 3:
                log(self.get_machine_log() + f"sent {len(new_edges.list_rep())} edges in heartbeat")
        comm.send(np.array(new_edges.list_rep()), dest=0, tag=MPI_TAG.HEARTBEAT.value)
        # log("heartbeat sent")

    def send_burn_requests(self):
        # log("in send burn requests")
        remote_vertices = self.fire.remote_vertices_to_burn
        machine_vertexes_to_receive = {}
        for machine in range(0, self.num_compute_nodes+1):
            machine_vertexes_to_receive[machine] = []

        for vert in remote_vertices:
            machine_owning_vertex = self.machine_with_vertex[vert]
            machine_vertexes_to_receive[machine_owning_vertex].append(vert)

        # log("machine_vertexes_to_receive = ")
        # for i in machine_vertexes_to_receive.keys():
        #     log(str(i) + " : " + str(machine_vertexes_to_receive[i]))

        self.send_fire_to_remotes(machine_vertexes_to_receive)
        self.fire.reset_remote_vertices_to_burn()


    def set_fire_step(self, new_fire_step):
        self.fire_step = max(min(new_fire_step, 32), 10)
        log(f"setting fire step to {self.fire_step}")

    def do_spread_steps(self, new_edges):
        # do 10 spread steps,
        # new_edges are updated every spread step by the fire
        for i in range(self.fire_step):
            self.fire.spread(new_edges)

    def init_partition(self, path_to_edge_file):
        for vert_1, vert_2 in self.graph_reader.read_graph_file(path_to_edge_file):
            self.partitioned_graph.add_vertex_and_neighbor(vert_1, vert_2)


    def reset_fire(self):
        self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.fire.ignite_random_node()


    def receive_from_headnode(self):
        # blocking receive from headnode.
        # log("about to receive from headnode")
        status = MPI.Status()
        data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag() == MPI_TAG.CONTINUE.value:
            pass
            # log("continuing")
        elif status.Get_tag() == MPI_TAG.KILL.value:
            # log(self.get_machine_log() + ".. reveived kill")
            self.fire.stop_burning()
            self.killed = True
        elif status.Get_tag() == MPI_TAG.RESET.value:
            self.reset_fire()
        # log("received from headnode")

    def do_tasks(self):
        # only ignites, has not started spreading
        # log(self.partitioned_graph.v_id_to_neighbors)
        self.fire.ignite_random_node()
        iterations = 0
        all_edges_sent = EdgeSet()
        while not self.killed:

            new_edges = EdgeSet()
            # log(self.get_machine_log() + ".. num_burning vertex ids = " + str(len(self.fire.get_burning_vertex_ids())))
            self.do_spread_steps(new_edges)

            if self.fires_wild:
                self.send_burn_requests()

            # log(self.get_machine_log() + ".. num edges sent = " + str(len(new_edges.list_rep())))
            for edge in new_edges.edges:
                all_edges_sent.add_edge(edge[0], edge[1])

            self.send_heartbeat(new_edges)
            self.receive_from_headnode()


        log("num edges sent total = " + str(len(all_edges_sent.list_rep())))
