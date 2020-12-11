import logging
import numpy as np
import mpi4py
mpi4py.rc.recv_mprobe = False
from mpi4py import MPI

from TimeIt import timeit
from Graph import Graph, GraphInterpreter
from Fire import Fire
from EdgeSet import EdgeSet
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES

comm = MPI.COMM_WORLD

# add function names here that needs timing
func_to_time = ["send_fire_to_remotes", "send_heartbeat", "send_burn_requests",
                "do_spread_steps", "init_partition", "receive_from_headnode", "do_tasks"]
timer = {func:0 for func in func_to_time}
counter = {func:0 for func in func_to_time}
counter["n_edge_in_send_heartbeat"] = 0


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

    def __del__(self):
        for k, v in timer.items():
            logging.info(f"timer {k} {v:.2f}")

        for k, v in counter.items():
            logging.info(f"counter {k} {v}")

    def get_machine_log(self):
        return "On Machine " + str(self.rank) + "."

    @timeit(timer=timer, counter=counter)
    def send_fire_to_remotes(self, machine_vertexes_to_receive):
        nodes_to_burn_locally = []
        logging.debug(self.get_machine_log() + " sending data")

        for i in range(1, self.num_compute_nodes+1):
            if i != self.rank:
                data = comm.sendrecv(machine_vertexes_to_receive[i],
                    dest=i ,
                    sendtag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value,
                    recvbuf=None,
                    source=i,
                    recvtag=MPI_TAG.FROM_COMPUTE_TO_COMPUTE.value,
                    status=None)
                if len(data) > 0:
                    nodes_to_burn_locally.extend(data)

        self.fire.merge(nodes_to_burn_locally)

    @timeit(timer=timer, counter=counter)
    def send_heartbeat(self, new_edges):
        # this send is non-blocking
        logging.debug("sending heartbeat")
        data = np.array(new_edges.list_rep())
        # record how many edges are sent
        counter["n_edge_in_send_heartbeat"] += data.shape[0]
        comm.send(data, dest=0, tag=MPI_TAG.HEARTBEAT.value)
        logging.debug("heartbeat sent")

    @timeit(timer=timer, counter=counter)
    def send_burn_requests(self):
        remote_vertices = self.fire.remote_vertices_to_burn
        machine_vertexes_to_receive = {}
        for machine in range(0, self.num_compute_nodes+1):
            machine_vertexes_to_receive[machine] = []

        for vert in remote_vertices:
            machine_owning_vertex = self.machine_with_vertex[vert]
            machine_vertexes_to_receive[machine_owning_vertex].append(vert)

        self.send_fire_to_remotes(machine_vertexes_to_receive)
        self.fire.reset_remote_vertices_to_burn()

    def set_fire_step(self, new_fire_step):
        self.fire_step = max(min(new_fire_step, 32), 10)
        logging.debug(f"setting fire step to {self.fire_step}")

    @timeit(timer=timer, counter=counter)
    def do_spread_steps(self, new_edges):
        # do 10 spread steps,
        # new_edges are updated every spread step by the fire
        for i in range(self.fire_step):
            self.fire.spread(new_edges)

    @timeit(timer=timer, counter=counter)
    def init_partition(self, path_to_edge_file):
        for vert_1, vert_2 in self.graph_reader.read_graph_file(path_to_edge_file):
            self.partitioned_graph.add_vertex_and_neighbor(vert_1, vert_2)

    def reset_fire(self):
        self.partitioned_graph.set_all_vertex_status(VertexStatus.NOT_BURNED)
        self.fire.ignite_random_node()

    @timeit(timer=timer, counter=counter)
    def receive_from_headnode(self):
        # blocking receive from headnode.
        logging.debug("about to receive from headnode")
        status = MPI.Status()
        comm.recv(source=0, tag=MPI.ANY_TAG, status=status)

        if status.Get_tag() == MPI_TAG.CONTINUE.value:
            logging.debug("continuing")
        elif status.Get_tag() == MPI_TAG.KILL.value:
            logging.debug(self.get_machine_log() + ".. received kill")
            self.fire.stop_burning()
            self.killed = True
        elif status.Get_tag() == MPI_TAG.RESET.value:
            self.reset_fire()
        logging.debug("received from headnode")

    @timeit(timer=timer, counter=counter)
    def do_tasks(self):
        # only ignites, has not started spreading
        self.fire.ignite_random_node()
        all_edges_sent = EdgeSet()
        while not self.killed:
            new_edges = EdgeSet()
            logging.debug(self.get_machine_log() + ".. num_burning vertex ids = " +
                          str(len(self.fire.get_burning_vertex_ids())))
            self.do_spread_steps(new_edges)

            if self.fires_wild:
                self.send_burn_requests()

            logging.debug(self.get_machine_log() + ".. num edges sent = " +
                          str(len(new_edges.list_rep())))

            for edge in new_edges.edges:
                all_edges_sent.add_edge(edge[0], edge[1])

            self.send_heartbeat(new_edges)
            self.receive_from_headnode()

        logging.debug("num edges sent total = " + str(len(all_edges_sent.list_rep())))
