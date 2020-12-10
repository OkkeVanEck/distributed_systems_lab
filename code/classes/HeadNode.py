import numpy as np
import itertools
import threading
import gzip
import time
import random

from HeadGraph import HeadGraph
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES


from mpi4py import MPI
comm = MPI.COMM_WORLD

DO_LOG=False

def log(message):
    if (DO_LOG):
        print(message)


class HeadNode:
    def __init__(self, rank, n_nodes, scale_factor, total_vertices, out_v, out_e, stitch=True, ring_stitch=True, connectivity=0.1):
        """
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.total_vertices = total_vertices
        self.need_stitch = stitch
        self.connectivity = connectivity
        self.ring_stitch = ring_stitch

        # scale factor 1 will be upscale sample that stays the same size
        if scale_factor < 1:
            self.num_sample = 1
            self.cutoff_vertices = total_vertices * scale_factor
            log("collecting " + str(self.cutoff_vertices) + " vertices")
            self.upscale = False
        else:
            self.num_sample = np.int(np.floor(scale_factor * 2))
            self.cutoff_vertices = total_vertices * (scale_factor / self.num_sample)
            self.upscale = True
        log("num samples is " + str(self.num_sample))

        self.graph = HeadGraph(total_vertices, self.num_sample, out_e, out_v)
        self.keep_burning = True

    def run(self):
        for cur_sample in range(self.num_sample):
            while self.keep_burning:
                log(f"sample {cur_sample}/{self.num_sample}, prog: {self.graph.get_num_sample_vertices(cur_sample)/self.cutoff_vertices}")
                tag = MPI_TAG.CONTINUE.value
                for i in range(1, self.num_compute_nodes+1):
                    log(f"one headnode. receiving from compute node {i}")
                    data = comm.recv(source=i, tag=MPI_TAG.HEARTBEAT.value)
                    log(data)
                    if tag == MPI_TAG.CONTINUE.value:
                        kl = 0 # debug
                        for [src, dest] in data:
                            self.graph.add_edge(src, dest, cur_sample)
                            kl += 1 # debug
                            if self.done_burning(cur_sample):
                                self.keep_burning = False
                                if cur_sample < self.num_sample-1:
                                    tag = MPI_TAG.RESET.value
                                    log(f"time to reset at compute={i} and element {kl}")
                                else:
                                    tag = MPI_TAG.KILL.value
                                    log(f"time to kill at compute={i} and element {kl}")
                                break
                log("Sending tags " + str(tag) + " | RESET = 4 | KILL = 5 | CONTINUE = 6")
                for i in range(1, self.num_compute_nodes+1):
                    comm.send(None, dest=i, tag=tag)
            self.graph.next_sample()
            self.keep_burning = True
        log("start stitch")
        self.stitch()
        log("end stitch")
        self.graph.write2file()

    def stitch(self):
        if not self.need_stitch:
            return
        if self.upscale:
            if self.ring_stitch:
                vertices = self.graph.get_vertices()
                for i in range(self.num_sample):
                    end = np.int(np.ceil(len(vertices[i])*self.connectivity))
                    while (end > 10000):
                        self.stitch_sample(vertices[i], vertices[(i+1) % self.num_sample], 10000)
                        end -= 10000
                    self.stitch_sample(vertices[i], vertices[(i+1) % self.num_sample], end)
            else:
                sample = self.graph.get_random_stitch_list()
                end = np.int(np.ceil(len(sample)*self.connectivity))
                while (end > 10000):
                    self.stitch_sample(sample, sample, 10000)
                    end -= 10000
                self.stitch_sample(sample, sample, end)
        else:
            sample = self.graph.get_vertices()[0]
            end = np.int(np.ceil(len(sample)*self.connectivity))
            for i in range(self.num_sample):
                end = np.int(np.ceil(len(vertices[i])*self.connectivity))
                while (end > 10000):
                    self.stitch_sample(sample, sample, 10000)
                    end -= 10000
                self.stitch_sample(sample, sample, end)

    def stitch_sample(self, src_sample, dest_sample, end):
        source = random.sample(src_sample, end)
        destination = random.sample(dest_sample, end)
        for (src, dest) in zip(source, destination):
            if src != dest:
                self.graph.add_edge(src, dest, None, 0)

    def done_burning(self, cur_sample):
        return self.graph.get_num_sample_vertices(cur_sample) >= self.cutoff_vertices
