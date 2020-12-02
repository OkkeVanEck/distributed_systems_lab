import numpy as np
import threading
import gzip
import time

from .HeadGraph import HeadGraph
from .Enums import MPI_TAG


from mpi4py import MPI
comm = MPI.COMM_WORLD

def log(message):
    if (False):
        print(message)


class HeadNode:
    def __init__(self, rank, n_nodes, scale_factor, total_vertices):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.graph = HeadGraph(total_vertices)

        # variable for stitching
        self.partition_center = [None] * num_compute_nodes
        self.centers = 0


        # TODO change for upscaling
        self.scale_factor = scale_factor
        self.cutoff_vertices = total_vertices * self.scale_factor

        self.keep_burning = True
        self.listen_thread = threading.Thread(target=self.listen, args=())

    def run(self):
        while self.keep_burning:
            sleep(2)
            if self.centers == self.num_compute_nodes:
                add_stitch(self)
            self.graph.write_to_file()
        self.graph.write_to_file()

    def add_stitch(self):
        for i in range(num_compute_nodes - 1);
            self.graph.add_edge(self.partition_center[i], self.partition_center[i+1])
        self.graph.add_edge(self.partition_center[num_compute_nodes-1], self.partition_center[0])

    def send_kill(self):
        for dest in range(1, num_compute_nodes+1):
            comm.send(None, dest=dest, tag=MPI_TAG.KILL.value)

    def send_restart(self):
        for dest in range(1, num_compute_nodes+1):
            comm.send(None, dest=dest, tag=MPI_TAG.RESTART.value)

    def listen(self):
        while self.keep_burning:
            log("checking if other messages arrived")
            self.listen_for_heartbeat()
            time.sleep(0.05)


    def listen_for_heartbeat(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.FROM_COMPUTE_TO_HEAD.value):
            status = MPI.Status()
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.FROM_COMPUTE_TO_HEAD.value, status=status)

            sender = status.Get_source() - 1
            if self.partition_center[sender] == None:
                self.partition_center[sender] = data[0,0]
                self.centers += 1

            for [src, dest] in data:
                self.graph.add_edge(src, dest)
                if self.done_burning():
                    self.send_kill()
                    self.keep_burning = False
                    break

    def done_burning():
        return graph.get_number_vertices() > self.cutoff_vertices
