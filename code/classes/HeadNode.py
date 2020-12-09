import numpy as np
import threading
import gzip
import time
import math

from HeadGraph import HeadGraph
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES


from mpi4py import MPI
comm = MPI.COMM_WORLD

DO_LOG=False

def log(message):
    if (DO_LOG):
        print(message)


class HeadNode:
    def __init__(self, rank, n_nodes, scale_factor, total_vertices, out_v, out_e):
        """
        NOTE: get_vertex_rank is a function. This way we can use this class in
                a flexible way.
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.total_vertices = total_vertices
        # variable for stitching
        self.partition_center = [None] * self.num_compute_nodes
        self.num_centers = 0

        # scale factor 1 will be upscale sample that stays the same size
        if scale_factor < 1:
            self.samples_remain = 1
            self.cutoff_vertices = total_vertices * scale_factor
        else:
            self.samples_remain = math.floor(scale_factor * 2)
            self.cutoff_vertices = total_vertices * (scale_factor / self.samples_remain)
        self.sample_center = [None] * self.samples_remain # gets filled back to front

        # to detect which sample a heartbeat belongs too
        self.need_ack = [False] * self.num_compute_nodes

        self.graph = HeadGraph(total_vertices, self.cutoff_vertices, out_e, out_v)

        self.keep_burning = True
        self.need_stitch = True
        self.listen_thread = threading.Thread(target=self.listen, args=())

    def run(self):
        self.listen_thread.start()
        while self.keep_burning or self.samples_remain > 0:
            if self.need_stitch and self.num_centers == self.num_compute_nodes: # this needs to change for relight
                self.add_stitch()
                self.need_stitch = False
            self.graph.write_to_file()
            time.sleep(2)
        self.change_center_to_final_id()
        self.add_sample_stitch()
        self.graph.write_to_file()
        self.listen_thread.join()

    def change_center_to_final_id(self):
        index = len(self.sample_center) - 1
        for i in range(len(self.sample_center)):
            self.sample_center[index - i] += i * self.total_vertices

    def add_stitch(self):
        center_list = [x for x in self.sample_center if x != None]
        if (len(center_list)) < 2:
            return
        for i in range(len(center_list) - 1):
            self.graph.add_edge(center_list[i], center_list[i+1])
        self.graph.add_edge(center_list[-1], center_list[0])

    def add_sample_stitch(self):
        center_list = [x for x in self.sample_center if x != None]
        if (len(center_list)) < 2:
            return
        for i in range(len(center_list) - 1):
            self.graph.add_edge(center_list[i], center_list[i+1], 0)
        self.graph.add_edge(center_list[-1], center_list[0], 0)

    def send_kill(self):
        for dest in range(1, self.num_compute_nodes+1):
            comm.send(None, dest=dest, tag=MPI_TAG.KILL_FROM_HEAD.value)

    def send_restart(self):
        for dest in range(1, self.num_compute_nodes+1):
            self.need_ack[dest-1] = True
            comm.send(None, dest=dest, tag=MPI_TAG.RESET_FROM_HEAD_TAG.value)

    def listen(self):
        while (self.samples_remain > 0):
            log(self.samples_remain)
            while self.keep_burning:
                self.listen_for_heartbeat()
                self.listen_for_ack()
                time.sleep(0.05)
            self.samples_remain -= 1
            self.keep_burning = True
            if self.samples_remain > 0:
                self.send_restart()
                self.graph.next_sample()
                self.partition_center = [None] * self.num_compute_nodes
                self.need_stitch = True
        self.keep_burning = False
        self.send_kill()

    def listen_for_heartbeat(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.HEARTBEAT.value):
            status = MPI.Status()
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.HEARTBEAT.value, status=status)
            sender = status.Get_source() - 1 # only works if head is rank 0
            log(f"{data}, sender: {sender}")

            # message is still received so computed node doesnt get into deadlock when sending message head doesnt want
            if self.need_ack[sender]:
                log("dont need this data from sender = " + str(sender))
                return

            if self.partition_center[sender] == None and len(data) > 0:
                self.partition_center[sender] = data[0,0]
                self.num_centers += 1

            if self.sample_center[self.samples_remain-1] == None and len(data) > 0:
                self.sample_center[self.samples_remain-1] = data[0,0]

            for [src, dest] in data:
                self.graph.add_edge(src, dest)
                if self.done_burning():
                    self.keep_burning = False
                    break

    def listen_for_ack(self):
        if comm.Iprobe(source=MPI.ANY_SOURCE,tag=MPI_TAG.RESET_ACK.value):

            status = MPI.Status()
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI_TAG.RESET_ACK.value, status=status)
            sender = status.Get_source() - 1 # only works if head is rank 0
            log("found ack. sender is = " + str(sender))
            self.need_ack[sender] = False

    def done_burning(self):
        return self.graph.get_sample_vertices() >= self.cutoff_vertices
